from pathlib import Path

from PySide6.QtGui import QFontDatabase

def load_fonts():
    project_root = Path(__file__).resolve().parents[3]

    lora_fonts = [
        "fonts/Lora/Lora-Regular.ttf",
        "fonts/Lora/Lora-SemiBold.ttf",
        "fonts/Lora/Lora-Bold.ttf",

        "fonts/Lora/Lora-Italic.ttf",
        "fonts/Lora/Lora-SemiBoldItalic.ttf",
        "fonts/Lora/Lora-BoldItalic.ttf",

        "fonts/Lora/Lora-Medium.ttf",
        "fonts/Lora/Lora-MediumItalic.ttf",
    ]

    nunito_fonts = [
        "fonts/Nunito_Sans/Nunito-Regular.ttf",
        "fonts/Nunito_Sans/Nunito-Medium.ttf",
        "fonts/Nunito_Sans/Nunito-SemiBold.ttf",
        "fonts/Nunito_Sans/Nunito-Bold.ttf",
    ]

    for font in lora_fonts:
        font_path = project_root / "fonts" / "lora" / font

        font_id = QFontDatabase.addApplicationFont(str(font_path))

    for font in nunito_fonts:
        font_path = project_root / "fonts" / "lora" / font
        
        font_id = QFontDatabase.addApplicationFont(str(font_path))