# etl_loader.py — ВЕРСИЯ 8.0 (простая логика: SELECT → INSERT, без ON CONFLICT)
import os
import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, inspect
from pathlib import Path
from urllib.parse import quote_plus
from tqdm import tqdm

def to_python_type(val):
    """Конвертирует numpy-типы в стандартные Python-типы для psycopg2"""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    return val

# 🔑 НАСТРОЙКИ
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'amurcodednk',
    'user': 'postgres',
    'password': '12345678'
}
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
BASE_DIR = Path("./data_cleared")


# 🧹 Утилиты
def clean_number(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r'[^\d.,-]', '', regex=True).str.replace(',', '.').astype(float)


def parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, format='%d.%m.%Y', dayfirst=True, errors='coerce').dt.date


def extract_snapshot(fname: str) -> str:
    months = {'январь': '01', 'февраль': '02', 'март': '03', 'апрель': '04', 'май': '05', 'июнь': '06',
              'июль': '07', 'август': '08', 'сентябрь': '09', 'октябрь': '10', 'ноябрь': '11', 'декабрь': '12'}
    for ru, num in months.items():
        if ru in fname.lower():
            match = re.search(r'(\d{4})', fname)
            year = match.group(1) if match else '2025'
            return f"{year}-{num}"
    return "unknown"


def table_exists(table_name: str) -> bool:
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            return table_name in inspector.get_table_names()
    except:
        return False


def reset_db():
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


def get_or_insert_dim_simple(series: pd.Series, table: str, col: str, pk_col: str) -> pd.DataFrame:
    """Простая логика: для каждого значения — SELECT, если нет — INSERT"""
    vals = series.dropna().astype(str).unique().tolist()
    if not vals:
        return pd.DataFrame(columns=[col, pk_col])

    with engine.begin() as conn:
        for val in vals:
            # SELECT: проверяем, существует ли запись
            result = conn.execute(
                text(f"SELECT {pk_col} FROM {table} WHERE {col} = :val LIMIT 1"),
                {"val": val}
            ).fetchone()
            # Если не найдено — INSERT
            if not result:
                conn.execute(
                    text(f"INSERT INTO {table} ({col}) VALUES (:val)"),
                    {"val": val}
                )

    # Возвращаем маппинг всех значений с их ID
    with engine.connect() as conn:
        return pd.read_sql(f"SELECT {col}, {pk_col} FROM {table}", conn)


def insert_fact_simple(df: pd.DataFrame, table: str, cols: list, unique_check_cols: list) -> int:
    """Простая построчная вставка с конвертацией типов"""
    if df.empty:
        return 0

    inserted = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            # 🔥 Конвертируем все значения в стандартные типы
            row_dict = {c: to_python_type(row[c]) for c in cols if c in row}

            # Формируем условие для проверки
            conditions = " AND ".join([f"{c} = :{c}" for c in unique_check_cols if c in row_dict])
            values = {c: row_dict[c] for c in unique_check_cols if c in row_dict}

            if not conditions:  # Если нет уникальных ключей — вставляем всегда
                result = None
            else:
                result = conn.execute(
                    text(f"SELECT 1 FROM {table} WHERE {conditions} LIMIT 1"),
                    values
                ).fetchone()

            if not result:
                insert_cols = ", ".join(cols)
                placeholders = ", ".join([f":{c}" for c in cols])
                conn.execute(
                    text(f"INSERT INTO {table} ({insert_cols}) VALUES ({placeholders})"),
                    row_dict
                )
                inserted += 1
    return inserted


def load_planning():
    """АЦК-Планирование: 1. РЧБ"""
    dir_path = BASE_DIR / "1. РЧБ"
    if not dir_path.exists():
        print("⚠️ Папка 1. РЧБ не найдена")
        return

    total_loaded = 0
    for f in sorted(dir_path.glob("*.csv")):
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

            # Справочники (простая логика)
            budgets = get_or_insert_dim_simple(df['Бюджет'], 'dim_budget', 'budget_name', 'budget_id')
            orgs = get_or_insert_dim_simple(df['Наименование КВСР'], 'dim_organization', 'org_name', 'org_id')

            # Классификация: составной ключ
            df['class_key'] = df['КЦСР'].astype(str) + '|' + df['КВР'].astype(str) + '|' + df['КОСГУ'].astype(str)
            classes = get_or_insert_dim_simple(df['class_key'], 'dim_classification', 'kcsr_code', 'class_id')

            # Маппинг
            fact = df.merge(budgets, left_on='Бюджет', right_on='budget_name', how='left')
            fact = fact.merge(orgs, left_on='Наименование КВСР', right_on='org_name', how='left')
            fact = fact.merge(classes, left_on='class_key', right_on='kcsr_code', how='left')
            fact = fact.rename(columns={'id_x': 'budget_id', 'id_y': 'org_id'})

            # 🔥 Вставка в fact_planning: простая построчная логика
            cols = ['posting_date', 'budget_id', 'org_id', 'limits_pbs', 'limits_remainder', 'snapshot_period',
                    'class_id']
            unique_keys = ['posting_date', 'budget_id', 'org_id', 'class_id',
                           'snapshot_period']  # уникальные поля для проверки
            inserted = insert_fact_simple(fact[cols], 'fact_planning', cols, unique_keys)
            total_loaded += inserted
            print(f"  ✅ {f.name}: {inserted} новых строк")

        except Exception as e:
            print(f"  ❌ Ошибка в {f.name}: {e}")

    print(f"✅ Планирование: всего загружено {total_loaded} новых строк.\n")


def load_execution():
    """АЦК-Финансы: 4. Выгрузка БУАУ"""
    dir_path = BASE_DIR / "4. Выгрузка БУАУ"
    if not dir_path.exists():
        print("⚠️ Папка 4. Выгрузка БУАУ не найдена")
        return

    total_loaded = 0
    for f in sorted(dir_path.glob("*.csv")):
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

            budgets = get_or_insert_dim_simple(df['Бюджет'], 'dim_budget', 'budget_name', 'budget_id')
            orgs = get_or_insert_dim_simple(df['Организация'], 'dim_organization', 'org_name', 'org_id')

            fact = df.merge(budgets, left_on='Бюджет', right_on='budget_name', how='left')
            fact = fact.merge(orgs, left_on='Организация', right_on='org_name', how='left')
            fact = fact.rename(columns={'id_x': 'budget_id', 'id_y': 'org_id'})

            cols = ['posting_date', 'budget_id', 'org_id', 'subsidy_code', 'payments_total', 'payments_execution',
                    'snapshot_period']
            unique_keys = ['posting_date', 'budget_id', 'org_id', 'subsidy_code', 'snapshot_period']
            inserted = insert_fact_simple(fact[cols], 'fact_execution', cols, unique_keys)
            total_loaded += inserted
            print(f"  ✅ {f.name}: {inserted} новых строк")

        except Exception as e:
            print(f"  ❌ Ошибка в {f.name}: {e}")

    print(f"✅ Исполнение: всего загружено {total_loaded} новых строк.\n")


def load_agreements():
    """2. Соглашения: документ-ориентированная структура"""
    dir_path = BASE_DIR / "2. Соглашения"
    if not dir_path.exists():
        print("⚠️ Папка 2. Соглашения не найдена")
        return

    total_loaded = 0
    for f in sorted(dir_path.glob("*.csv")):
        print(f"📄 Обработка {f.name}...")
        try:
            # Читаем CSV
            df = pd.read_csv(f, encoding='utf-8-sig', on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]

            # Проверка обязательных полей
            required = ['document_id', 'caption', 'dd_recipient_caption', 'kcsr_code']
            missing = [c for c in required if c not in df.columns]
            if missing:
                print(f"  ⚠️ Не найдены: {missing}")
                continue

            # Очистка и подготовка
            df = df[df['document_id'].notna()]
            df['close_date'] = pd.to_datetime(df['close_date'], errors='coerce').dt.date
            df['amount_1year'] = clean_number(df['amount_1year'])

            # Извлекаем snapshot_period
            def extract_period_from_range(period_str):
                if pd.isna(period_str):
                    return "unknown"
                date_part = str(period_str).split(' - ')[0]
                try:
                    dt = pd.to_datetime(date_part)
                    return f"{dt.year}-{dt.month:02d}"
                except:
                    return "unknown"

            df['snapshot_period'] = df['period_of_date'].apply(extract_period_from_range)
            df = df.dropna(subset=['close_date'])

            # Справочники
            budgets = get_or_insert_dim_simple(df['caption'], 'dim_budget', 'budget_name', 'budget_id')
            orgs = get_or_insert_dim_simple(df['dd_recipient_caption'], 'dim_organization', 'org_name', 'org_id')

            # Классификация
            df['class_key'] = (
                    df['kcsr_code'].astype(str) + '|' +
                    df['kvr_code'].astype(str) + '|' +
                    df['kesr_code'].astype(str)
            )
            classes = get_or_insert_dim_simple(df['class_key'], 'dim_classification', 'kcsr_code', 'class_id')

            # 🔥 Документы: конвертируем типы перед вставкой
            docs = df[['document_id', 'reg_number', 'close_date', 'documentclass_id']].drop_duplicates()
            with engine.begin() as conn:
                for _, doc in docs.iterrows():
                    doc_id = str(doc['document_id']) if pd.notna(doc['document_id']) else None
                    doc_class = f"class_{int(doc['documentclass_id'])}" if pd.notna(
                        doc['documentclass_id']) else 'unknown'
                    reg_num = str(doc['reg_number']) if pd.notna(doc['reg_number']) else None
                    close_dt = doc['close_date']

                    # Получаем budget_id
                    budget_name = df.loc[df['document_id'] == doc['document_id'], 'caption'].iloc[0]
                    budget_row = budgets[budgets['budget_name'] == budget_name]
                    budget_id = int(budget_row['budget_id'].iloc[0]) if not budget_row.empty else None

                    # Проверка существования
                    result = conn.execute(
                        text("SELECT 1 FROM dim_document WHERE document_id = :doc_id LIMIT 1"),
                        {"doc_id": doc_id}
                    ).fetchone()

                    if not result:
                        # 🔥 Конвертируем ВСЕ параметры через to_python_type
                        params = {
                            "doc_id": to_python_type(doc_id),
                            "doc_class": to_python_type(doc_class),
                            "reg_num": to_python_type(reg_num),
                            "close_dt": to_python_type(close_dt),
                            "budget_id": to_python_type(budget_id)
                        }
                        conn.execute(
                            text("""
                                INSERT INTO dim_document 
                                (document_id, document_class, reg_number, close_date, budget_id) 
                                VALUES (:doc_id, :doc_class, :reg_num, :close_dt, :budget_id)
                            """),
                            params
                        )

            # 🔥 Маппинг для fact_agreements
            fact = df.merge(budgets, left_on='caption', right_on='budget_name', how='left')
            fact = fact.merge(orgs, left_on='dd_recipient_caption', right_on='org_name', how='left')
            fact = fact.merge(classes, left_on='class_key', right_on='kcsr_code', how='left')
            fact = fact.rename(columns={'id_x': 'budget_id', 'id_y': 'org_id'})

            # 🔥 Конвертируем числовые колонки в стандартные типы
            for col in ['budget_id', 'org_id', 'class_id']:
                if col in fact.columns:
                    fact[col] = fact[col].apply(to_python_type)
            if 'amount_1year' in fact.columns:
                fact['amount_1year'] = fact['amount_1year'].apply(to_python_type)

            # Вставка в fact_agreements
            cols = [
                'document_id', 'class_id', 'org_id',
                'amount_1year', 'dd_estimate_caption',
                'kadmr_code', 'kfsr_code', 'kcsr_code', 'kvr_code',
                'dd_purposefulgrant_code', 'kesr_code',
                'snapshot_period'
            ]
            unique_keys = ['document_id', 'snapshot_period']
            inserted = insert_fact_simple(fact[cols], 'fact_agreements', cols, unique_keys)
            total_loaded += inserted
            print(f"  ✅ {f.name}: {inserted} новых строк")

        except Exception as e:
            print(f"  ❌ Ошибка в {f.name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"✅ Соглашения: всего загружено {total_loaded} новых строк.\n")


def load_procurement():
    print("⏳ Загрузка госзаказа: требует объединения 3 файлов")


if __name__ == "__main__":
    import sys

    if "--reset" in sys.argv:
        reset_db()
        sys.exit(0)

    print("🚀 Запуск ETL...\n")
    load_planning()
    load_execution()
    load_agreements()
    load_procurement()
    print("\n🎉 ETL завершён.")