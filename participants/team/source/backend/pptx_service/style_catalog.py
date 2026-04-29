from pathlib import Path
from typing import Dict, List, Any

class StyleCatalog:
    def __init__(self, styles_folder: str = "styles"):
        self.styles_folder = Path(styles_folder)
        self.styles_folder.mkdir(exist_ok=True)
        
        self.presets = {
            "corporate": {
                "style_name": "Корпоративный",
                "palette": [(0, 51, 102), (255, 106, 0), (255, 255, 255)],
                "fonts": {"font_family": "Arial", "title_size_pt": 36, "body_size_pt": 18},
                "background_color": (255, 255, 255)
            },
            "minimal": {
                "style_name": "Минимализм",
                "palette": [(0, 0, 0), (100, 100, 100), (255, 255, 255)],
                "fonts": {"font_family": "Calibri", "title_size_pt": 40, "body_size_pt": 20},
                "background_color": (255, 255, 255)
            },
            "creative": {
                "style_name": "Креатив",
                "palette": [(125, 58, 255), (255, 107, 0), (255, 255, 255)],
                "fonts": {"font_family": "Verdana", "title_size_pt": 38, "body_size_pt": 18},
                "background_color": (250, 240, 230)
            },
            "dark_mode": {
                "style_name": "Тёмная тема",
                "palette": [(255, 255, 255), (125, 58, 255), (30, 30, 30)],
                "fonts": {"font_family": "Segoe UI", "title_size_pt": 36, "body_size_pt": 18},
                "background_color": (30, 30, 30)
            },
            "salatik_burmaldatik": {
                "style_name": "Салатик Бурмалдатик",
                "palette": [(144, 238, 144), (255, 182, 193), (255, 255, 224)],
                "fonts": {"font_family": "Comic Sans MS", "title_size_pt": 34, "body_size_pt": 16},
                "background_color": (255, 255, 224)
            }
        }
    
    def get_style_data(self, style_id: str) -> Dict[str, Any] | None:
        if style_id in self.presets:
            return self.presets[style_id]
        return None
