# coordinates.py

# Coordinates mapped on the 1000 x 1414 pixels (A4 aspect ratio) template
COORDINATES = {
    "name": (340, 505),
    "father": (340, 560),
    "mother": (340, 615),
    "class": (340, 665),
    "aadhaar": (340, 717),
    "registration": (340, 770),
    "mobile": (340, 820),
    "dob": (340, 873),
    "address": (340, 921),
    "photo": (50, 257),
    "male_checkbox": (715, 880),
    "female_checkbox": (825, 880)
}

# General settings for dynamic rendering
FONT_SETTINGS = {
    "font_dir": "fonts",
    "default_font": "Roboto.ttf",
    "default_size": 22,
    "font_color": (10, 16, 32),  # #0a1020 Dark Navy/Black
    "size_overrides": {
        "address": 16,
    }
}

PHOTO_SETTINGS = {
    "width": 178,
    "height": 227,
}
