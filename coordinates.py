# coordinates.py

# Coordinates mapped on the 1000 x 1414 pixels (A4 aspect ratio) template
COORDINATES = {
    "name": (340, 520),
    "father": (340, 575),
    "mother": (340, 630),
    "class": (340, 680),
    "aadhaar": (340, 732),
    "registration": (340, 785),
    "mobile": (340, 835),
    "dob": (340, 888),
    "address": (340, 936),
    "photo": (50, 257),
    "male_checkbox": (715, 895),
    "female_checkbox": (825, 895)
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
