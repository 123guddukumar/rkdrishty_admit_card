from openpyxl.cell import rich_text
import os
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from django.core.files.base import ContentFile
from django.conf import settings
from coordinates import COORDINATES, FONT_SETTINGS, PHOTO_SETTINGS

def crop_and_resize_photo(photo_file, target_w, target_h):
    """
    Intelligently crop and resize the photo to fit the box dimensions (target_w, target_h).
    It cuts extra width/height from sides/bottom to maintain aspect ratio and keep the subject centered.
    """
    img = Image.open(photo_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    target_ratio = target_w / target_h
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is too wide: crop sides
        new_width = int(target_ratio * img.height)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    elif img_ratio < target_ratio:
        # Image is too tall: crop from top/bottom (crop 20% from top, 80% from bottom to preserve face)
        new_height = int(img.width / target_ratio)
        offset_top = int((img.height - new_height) * 0.2)
        img = img.crop((0, offset_top, img.width, offset_top + new_height))

    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

def generate_admit_card_files(student, verification_url=None):
    """
    Generates high-quality JPG and PDF admit cards for the given student.
    Returns: (jpg_content_file, pdf_content_file)
    """
    # Look for template.jpg or template.png (JPG has priority)
    template_path = None
    possible_paths = [
        os.path.join(settings.MEDIA_ROOT, 'templates', 'template.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'templates', 'template.png'),
        os.path.join(settings.BASE_DIR, 'template.jpg'),
        os.path.join(settings.BASE_DIR, 'template.png'),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            template_path = path
            break

    if not template_path:
        raise FileNotFoundError("Admit card template (template.jpg or template.png) not found.")

    # 1. Open template and resize to A4 coordinate canvas (1000 x 1414)
    with Image.open(template_path) as base_img:
        card_img = base_img.resize((1000, 1414), Image.Resampling.LANCZOS)
        print(base_img.size)
        
    draw = ImageDraw.Draw(card_img)

    # 2. Load Font Settings
    font_dir = FONT_SETTINGS.get("font_dir", "fonts")
    default_font_name = FONT_SETTINGS.get("default_font", "Arial.ttf")
    default_size = FONT_SETTINGS.get("default_size", 22)
    font_color = FONT_SETTINGS.get("font_color", (10, 16, 32))

    def get_font(field_name):
        font_name = default_font_name
        size = FONT_SETTINGS.get("size_overrides", {}).get(field_name, default_size)
        font_path = os.path.join(settings.BASE_DIR, font_dir, font_name)
        
        # Fallback system fonts if files are missing
        if not os.path.exists(font_path):
            fallback_paths = [
                os.path.join("C:\\Windows\\Fonts", font_name),
                os.path.join("C:\\Windows\\Fonts", "arial.ttf"),
            ]
            for fb in fallback_paths:
                if os.path.exists(fb):
                    font_path = fb
                    break

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file missing: {font_path}. Please install Arial.ttf, Poppins.ttf, or Roboto.ttf in fonts/")
        
        return ImageFont.truetype(font_path, size)


    # 3. Paste Student Photo
    if student.photo:
        try:
            photo_w = PHOTO_SETTINGS.get("width", 200)
            photo_h = PHOTO_SETTINGS.get("height", 259)
            photo_coords = COORDINATES.get("photo", (50, 257))

            # Crop & Resize photo
            processed_photo = crop_and_resize_photo(
                student.photo.path,
                photo_w,
                photo_h
            ).convert("RGBA")

            # Create rounded mask
            radius = 5  # 5px radius
            mask = Image.new("L", (photo_w, photo_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (photo_w, photo_h)],
                radius=radius,
                fill=255
            )

            # Apply mask
            processed_photo.putalpha(mask)

            # Paste with transparency
            card_img.paste(processed_photo, photo_coords, processed_photo)

        except Exception as e:
            print(f"Error processing student photo: {e}")
    # 4. QR Code: Disabled (Keeping template's original QR code)
    pass

    # 5. Draw Checkbox Ticks for Gender (Manual line-drawn green checkmarks)
    try:
        green_color = (37, 162, 68)  # Forest Green
        if student.gender == 'Male':
            male_coords = COORDINATES.get("male_checkbox", (715, 900))
            cx, cy = male_coords
            draw.line(
                [(cx + 3, cy + 14), (cx + 10, cy + 21)],
                fill=green_color,
                width=5
            )

            draw.line(
                [(cx + 10, cy + 21), (cx + 22, cy + 5)],
                fill=green_color,
                width=5
            )
        elif student.gender == 'Female':
            female_coords = COORDINATES.get("female_checkbox", (825, 900))
            cx, cy = female_coords
            draw.line(
                [(cx + 3, cy + 14), (cx + 10, cy + 21)],
                fill=green_color,
                width=5
            )

            draw.line(
                [(cx + 10, cy + 21), (cx + 22, cy + 5)],
                fill=green_color,
                width=5
            )
    except Exception as e:
        print(f"Error ticking gender checkbox for {student.name}: {e}")



    # 6. Draw Student Details Text
    # Paint white rectangle over the address dotted line to remove it
    draw.rectangle([340, 955, 930, 970], fill=(255, 255, 255))

    fields = {
        "name": student.name,
        "father": student.father_name,
        "mother": student.mother_name,
        "class": student.student_class,
        "aadhaar": student.aadhaar_number,
        "registration": student.registration_number,
        "mobile": student.mobile_number,

        "dob": student.dob.strftime('%d/%m/%Y') if student.dob else "",
        "address": student.address
    }

    for field, val in fields.items():
        coords = COORDINATES.get(field)
        if coords:
            try:
                font = get_font(field)
                # Handle multi-line addresses
                if field == "address":
                    lines = []
                    words = str(val).split()
                    current_line = ""
                    for word in words:
                        test_line = f"{current_line} {word}".strip()
                        # Wrap line if it is too long (approx 45 characters max for address field width)
                        if len(test_line) > 42:
                            lines.append(current_line)
                            current_line = word
                        else:
                            current_line = test_line
                    if current_line:
                        lines.append(current_line)
                    
                    y_offset = 0
                    for line in lines[:2]:  # Limit to 2 lines to fit without overlap
                        draw.text((coords[0], coords[1] + y_offset), line, fill=font_color, font=font)
                        y_offset += 24
                else:
                    draw.text(coords, str(val), fill=font_color, font=font)
            except Exception as e:
                print(f"Error drawing text field {field} for {student.name}: {e}")

    # 7. Export JPG bytes in-memory
    jpg_buffer = io.BytesIO()
    card_img.save(jpg_buffer, format='JPEG', quality=95)
    jpg_data = jpg_buffer.getvalue()
    
    # 8. Export PDF bytes in-memory using ReportLab
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    # A4 size is exactly 595.27 x 841.89 points
    c.drawImage(ImageReader(Image.open(io.BytesIO(jpg_data))), 0, 0, width=595.27, height=841.89)
    c.showPage()
    c.save()
    pdf_data = pdf_buffer.getvalue()

    filename_base = f"{student.name.replace(' ', '_')}_{student.registration_number}"
    
    jpg_content = ContentFile(jpg_data, name=f"{filename_base}.jpg")
    pdf_content = ContentFile(pdf_data, name=f"{filename_base}.pdf")

    return jpg_content, pdf_content

