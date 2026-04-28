# etl_loader.py — ВЕРСИЯ 6.0 (исправленная под data_cleared и ON CONFLICT)
import os
import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, inspect
from pathlib import Path
from urllib.parse import quote_plus
from tqdm import tqdm

# 🔑 НАСТРОЙКИ
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'amurcodednk',  # или amurcodeDNK — как создали
    'user': 'postgres',
    'password': '12345678'
}
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
# 🔥 Изменено на data_cleared
BASE_DIR = Path("./data_cleared")


# 🧹 Утилиты
def clean_number(series: pd.Series) -> pd.Series:
    """Приводит русские форматы чисел к float"""
    return series.astype(str).str.replace(r'[^\d.,-]', '', regex=True).str.replace(',', '.').astype(float)


def parse_date(series: pd.Series) -> pd.Series:
    """Приводит даты к YYYY-MM-DD — ИСПРАВЛЕНО: dayfirst=True"""
    return pd.to_datetime(series, format='%d.%m.%Y', dayfirst=True, errors='coerce').dt.date


def extract_snapshot(fname: str) -> str:
    """Извлекает 'ГГГГ-ММ' из имени файла"""
    months = {'январь': '01', 'февраль': '02', 'март': '03', 'апрель': '04', 'май': '05', 'июнь': '06',
              'июль': '07', 'август': '08', 'сентябрь': '09', 'октябрь': '10', 'ноябрь': '11', 'декабрь': '12'}
    for ru, num in months.items():
        if ru in fname.lower():
            match = re.search(r'(\d{4})', fname)
            year = match.group(1) if match else '2025'
            return f"{year}-{num}"
    return "unknown"


def table_exists(table_name: str) -> bool:
    """Проверяет существование таблицы"""
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            return table_name in inspector.get_table_names()
    except:
        return False


def reset_db():
    """Безопасная очистка БД"""
    if not table_exists('fact_planning'):
        print("⚠️ Таблицы ещё не созданы. Сначала выполните db_schema.sql")
        return
    print("🧹 Очистка таблиц БД...")
    with engine.begin() as conn:
        conn.execute(text("""
            TRUNCATE fact_procurement, fact_agreements, fact_execution, fact_planning, 
                     dim_document, dim_classification, dim_organization, dim_budget 
            RESTART IDENTITY CASCADE;
        """))
    print("✅ База очищена.\n")


def get_or_insert_dim_safe(series: pd.Series, table: str, col: str, pk_col: str,
                           unique_cols: list = None) -> pd.DataFrame:
    """
    Безопасная загрузка справочника.
    unique_cols — список колонок для составного уникального ограничения (если есть)
    """
    vals = series.dropna().astype(str).unique().tolist()
    if not vals:
        return pd.DataFrame(columns=[col, pk_col])

    with engine.begin() as conn:
        for val in vals:
            if unique_cols:
                # Для составных уникальных ограничений: проверяем через SELECT
                result = conn.execute(
                    text(f"SELECT {pk_col} FROM {table} WHERE {col} = :val LIMIT 1"),
                    {"val": val}
                ).fetchone()
                if not result:
                    # Вставляем, если не найдено
                    try:
                        conn.execute(
                            text(f"INSERT INTO {table} ({col}) VALUES (:val)"),
                            {"val": val}
                        )
                    except:
                        pass  # Игнорируем дубликаты, если возникли между проверкой и вставкой
            else:
                # Для простых уникальных ограничений: ON CONFLICT
                conn.execute(
                    text(f"INSERT INTO {table} ({col}) VALUES (:val) ON CONFLICT ({col}) DO NOTHING"),
                    {"val": val}
                )

    # Возвращаем маппинг
    with engine.connect() as conn:
        return pd.read_sql(f"SELECT {col}, {pk_col} FROM {table}", conn)


# 📥 Загрузчики
def load_planning():
    """АЦК-Планирование: 1. РЧБ"""
    dir_path = BASE_DIR / "1. РЧБ"
    if not dir_path.exists():
        print("⚠️ Папка 1. РЧБ не найдена")
        return

    dfs = []
    for f in dir_path.glob("*.csv"):
        print(f"📄 Обработка {f.name}...")
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]

            required = ['Бюджет', 'Дата проводки', 'КЦСР', 'КВР', 'КОСГУ']
            missing = [c for c in required if c not in df.columns]
            if missing:
                print(f"  ⚠️ Не найдены: {missing}")
                continue

            df = df[(df['Бюджет'] != 'Итого') & (df['Бюджет'].notna())]
            df['posting_date'] = parse_date(df['Дата проводки'])

            year = extract_snapshot(f.name).split('-')[0]
            col_limits = [c for c in df.columns if 'Лимиты ПБС' in c and year in c]
            col_remainder = [c for c in df.columns if 'Остаток лимитов' in c and year in c]

            df['limits_pbs'] = clean_number(df[col_limits[0]]) if col_limits else pd.Series([0.0] * len(df))
            df['limits_remainder'] = clean_number(df[col_remainder[0]]) if col_remainder else pd.Series([0.0] * len(df))
            df['snapshot_period'] = extract_snapshot(f.name)

            df = df.dropna(subset=['posting_date'])
            dfs.append(df)
        except Exception as e:
            print(f"  ❌ Ошибка в {f.name}: {e}")

    if not dfs:
        print("⚠️ Нет данных для fact_planning")
        return

    full = pd.concat(dfs).drop_duplicates(
        subset=['Бюджет', 'Наименование КВСР', 'КЦСР', 'КВР', 'КОСГУ', 'Дата проводки', 'snapshot_period']
    )

    # Справочники
    budgets = get_or_insert_dim_safe(full['Бюджет'], 'dim_budget', 'budget_name', 'budget_id')
    orgs = get_or_insert_dim_safe(full['Наименование КВСР'], 'dim_organization', 'org_name', 'org_id')

    # 🔥 Классификация: составной уникальный ключ → передаём unique_cols
    full['class_key'] = full['КЦСР'].astype(str) + '|' + full['КВР'].astype(str) + '|' + full['КОСГУ'].astype(str)
    classes = get_or_insert_dim_safe(
        full['class_key'],
        'dim_classification',
        'kcsr_code',  # колонка для вставки
        'class_id',  # PK
        unique_cols=['kcsr_code', 'kvr_code', 'kosgu_code']  # составной UNIQUE
    )

    # Маппинг
    fact = full.merge(budgets, left_on='Бюджет', right_on='budget_name', how='left')
    fact = fact.merge(orgs, left_on='Наименование КВСР', right_on='org_name', how='left')
    fact = fact.merge(classes, left_on='class_key', right_on='kcsr_code', how='left')

    cols = ['posting_date', 'budget_id', 'org_id', 'Источник средств', 'limits_pbs', 'limits_remainder',
            'snapshot_period', 'class_id']
    fact[cols].to_sql('fact_planning', engine, if_exists='append', index=False, method='multi')
    print(f"✅ Планирование: {len(fact)} строк загружено.\n")


def load_execution():
    """АЦК-Финансы: 4. Выгрузка БУАУ"""
    dir_path = BASE_DIR / "4. Выгрузка БУАУ"
    if not dir_path.exists():
        print("⚠️ Папка 4. Выгрузка БУАУ не найдена (пропущено)")
        return

    dfs = []
    for f in dir_path.glob("*.csv"):
        print(f"📄 Обработка {f.name}...")
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]

            if 'Бюджет' not in df.columns:
                continue
            df = df[(df['Бюджет'] != 'Итого') & (df['Бюджет'].notna())]

            df['posting_date'] = parse_date(df['Дата проводки'])
            df['payments_execution'] = clean_number(df.get('Выплаты - Исполнение', pd.Series([0.0] * len(df))))
            df['payments_total'] = clean_number(df.get('Выплаты с учетом возврата', pd.Series([0.0] * len(df))))
            df['snapshot_period'] = extract_snapshot(f.name)

            df = df.dropna(subset=['posting_date'])
            dfs.append(df)
        except Exception as e:
            print(f"  ❌ Ошибка в {f.name}: {e}")

    if not dfs:
        print("⚠️ Нет данных для fact_execution")
        return

    full = pd.concat(dfs).drop_duplicates(
        subset=['Бюджет', 'Организация', 'КЦСР', 'КВР', 'КОСГУ', 'Дата проводки', 'snapshot_period']
    )

    budgets = get_or_insert_dim_safe(full['Бюджет'], 'dim_budget', 'budget_name', 'budget_id')
    orgs = get_or_insert_dim_safe(full['Организация'], 'dim_organization', 'org_name', 'org_id')

    fact = full.merge(budgets, left_on='Бюджет', right_on='budget_name', how='left')
    fact = fact.merge(orgs, left_on='Организация', right_on='org_name', how='left')

    cols = ['posting_date', 'budget_id', 'org_id', 'Код субсидии', 'payments_total', 'payments_execution',
            'snapshot_period']
    fact[cols].to_sql('fact_execution', engine, if_exists='append', index=False, method='multi')
    print(f"✅ Исполнение: {len(fact)} строк загружено.\n")


def load_agreements():
    print("⏳ Загрузка соглашений: требует анализа структуры")


def load_procurement():
    print("⏳ Загрузка госзаказа: требует объединения 3 файлов")


if __name__ == "__main__":
    import sys

    if "--reset" in sys.argv:
        reset_db()
        sys.exit(0)

    # 🔧 Для отладки: закомментируйте, чтобы не очищать БД каждый раз
    # reset_db()

    print("🚀 Запуск ETL...\n")
    load_planning()
    load_execution()
    load_agreements()
    load_procurement()
    print("\n🎉 ETL завершён.")