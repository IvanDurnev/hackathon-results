class ThemeService:
    """
    Dynamic Theme Engine
    Gamma-style theme system
    """

    def __init__(self):
        self.themes = {
            "startup": {
                "name": "Startup Investor Deck",
                "primary_color": (15, 23, 42),
                "accent_color": (59, 130, 246),
                "text_color": (71, 85, 105),
                "background": "dark",
                "font_style": "modern",
                "visual_mood": "executive"
            },

            "corporate": {
                "name": "Corporate Professional",
                "primary_color": (255, 255, 255),
                "accent_color": (37, 99, 235),
                "text_color": (51, 65, 85),
                "background": "light",
                "font_style": "clean",
                "visual_mood": "business"
            },

            "medical": {
                "name": "Medical Clean",
                "primary_color": (255, 255, 255),
                "accent_color": (16, 185, 129),
                "text_color": (55, 65, 81),
                "background": "light",
                "font_style": "clean",
                "visual_mood": "trust"
            },

            "finance": {
                "name": "Finance Executive",
                "primary_color": (17, 24, 39),
                "accent_color": (14, 165, 233),
                "text_color": (229, 231, 235),
                "background": "dark",
                "font_style": "executive",
                "visual_mood": "serious"
            },

            "education": {
                "name": "Education Modern",
                "primary_color": (255, 255, 255),
                "accent_color": (124, 58, 237),
                "text_color": (55, 48, 163),
                "background": "light",
                "font_style": "friendly",
                "visual_mood": "learning"
            },

            "luxury": {
                "name": "Luxury Premium",
                "primary_color": (10, 10, 10),
                "accent_color": (212, 175, 55),
                "text_color": (245, 245, 245),
                "background": "dark",
                "font_style": "premium",
                "visual_mood": "luxury"
            }
        }

    def detect_theme(self, prompt: str, style: str = ""):
        """
        Автоматическое определение темы
        """

        text = f"{prompt} {style}".lower()

        if any(word in text for word in [
            "startup", "pitch", "investor", "investment",
            "saas", "product", "venture"
        ]):
            return self.themes["startup"]

        elif any(word in text for word in [
            "medical", "medicine", "health",
            "hospital", "clinic", "doctor"
        ]):
            return self.themes["medical"]

        elif any(word in text for word in [
            "finance", "bank", "investment",
            "fintech", "economy", "financial"
        ]):
            return self.themes["finance"]

        elif any(word in text for word in [
            "education", "school", "university",
            "learning", "student", "course"
        ]):
            return self.themes["education"]

        elif any(word in text for word in [
            "luxury", "premium", "fashion",
            "brand", "vip", "exclusive"
        ]):
            return self.themes["luxury"]

        elif any(word in text for word in [
            "business", "company", "enterprise",
            "corporate", "presentation"
        ]):
            return self.themes["corporate"]

        return self.themes["startup"]

    def get_theme(self, prompt: str, style: str = ""):
        """
        Главный метод
        """

        theme = self.detect_theme(prompt, style)

        print(f"Theme selected: {theme['name']}")

        return theme