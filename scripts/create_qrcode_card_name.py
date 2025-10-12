import csv
import os
import re
import sys
import traceback
from pathlib import Path
import platform

import qrcode
from PIL import Image, ImageDraw, ImageFont

def sanitize_filename(filename):
    """Remove or replace invalid filename characters"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def wrap_text_to_lines(text, max_chars=12):
    """Wrap text to lines with maximum character limit"""
    if not text or len(text) <= max_chars:
        return [text] if text else []
    
    words = text.split()
    lines = []
    current = ""
    
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    
    if current:
        lines.append(current)
    
    return lines


def create_and_position_qr(qr_img, background):
    """Create QR code image and position it on the background"""
    # Resize QR code to fit nicely on card (adjust size as needed)
    qr_size = 450  # pixels
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Calculate position based on percentage from edges
    bg_width, bg_height = background.size

    # Simple positioning settings (adjust these percentages)
    horizontal_percent = (
        32  # % from left edge (0% = left, 100% = right)
    )
    vertical_percent = 60  # % from top edge (0% = top, 100% = bottom)

    # Calculate QR position (center the QR at the percentage point)
    qr_x = int(bg_width * horizontal_percent / 100) - (qr_size // 2)
    qr_y = int(bg_height * vertical_percent / 100) - (qr_size // 2)

    # === Paste QR code onto background ===
    background.paste(qr_img, (qr_x, qr_y))
    return background


def draw_name_text(draw, background, saint_name, last_name, first_name, note):
    """Draw name text: saint name wrapped at 12 chars, rest wrapped at 12 chars"""
    # Get background dimensions
    bg_width, bg_height = background.size
    
    # Text positioning settings (adjust these percentages)
    text_horizontal_percent = 77  # % from left edge (centered)
    text_vertical_percent = 50  # % from top edge

    # Calculate text position
    text_x = int(bg_width * text_horizontal_percent / 100)
    text_y = int(bg_height * text_vertical_percent / 100)

    # Get font: macOS uses Arial Bold, Linux uses DejaVu Sans Bold
    if platform.system() == "Darwin":  # macOS
        font_path = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf").resolve()
        font = ImageFont.truetype(str(font_path), 60)
    else:  # Linux
        font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf").resolve()
        font = ImageFont.truetype(str(font_path), 55)

    lines = []
    remaining = f"{last_name} {first_name} {note}".strip()

    # Apply 12-char line breaking using helper function
    lines.extend(wrap_text_to_lines(saint_name, 12))
    lines.extend(wrap_text_to_lines(remaining, 12))

    # Draw centered text block
    line_spacing = 60
    start_y = text_y - ((len(lines) - 1) * line_spacing // 2)

    for i, line in enumerate(lines):
        draw.text(
            (text_x, start_y + i * line_spacing),
            line,
            font=font,
            fill="black",
            anchor="ma",
        )


def main():
    # Check if CSV file path is provided
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage:   python3 (my_script_name)                   (my_input_data)")
        print("Example: python3 scripts/create_qrcode_card_name.py data/csv_files/2025_26/c1.csv")
        sys.exit(1)

    # Check if the CSV file exists
    if not os.path.exists(sys.argv[1]):
        print(f"❌ Error: CSV file not found")
        sys.exit(1)
    csv_input_path = sys.argv[1]
    csv_filename = Path(csv_input_path).stem

    # Check for background image
    background_path = f"data/card_background/{csv_filename}.png"
    if not os.path.exists(background_path):
        # Try alternative naming pattern
        background_path = f"data/card_background/{csv_filename}_background.png"
        if not os.path.exists(background_path):
            print(f"❌ Error: Background image not found at:")
            print(f"   - data/card_background/{csv_filename}.png")
            print(f"   - data/card_background/{csv_filename}_background.png")
            sys.exit(1)

    print(f"🖼️  Using background: {background_path}")

    # Determine output path
    if len(sys.argv) == 3:
        # Custom output path provided
        output_path = sys.argv[2]
    else:
        # Default: use CSV filename as directory name
        output_path = f"output/{csv_filename}"

    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    print(f"📁 Creating QR codes in directory: {output_path}/")

    # Count generated QR codes
    qr_count = 0

    # Read children data from the provided CSV file
    try:
        with open(csv_input_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            for index, row in enumerate(csv_reader):
                # only process row with student record (e.g. | 1 | Têrêsa Calcutta | Trần Di An |)
                # TODO: adjust số thứ tự (STT) column index if needed to match the CSV structure
                column_index = 1

                # Check if note field contains a date (e.g. 06/08/2019, 06-08-2019)
                # use this to classify same name students in the same class 
                note = row[column_index-1].strip() 
                note = note if re.match(r'\d{1,2}/\d{1,2}/\d{4}', note) else ""

                saint_name = row[column_index+1].strip() # Têrêsa Calcutta
                last_name = row[column_index+2].strip() # Trần Di
                first_name = row[column_index+3].strip() # An

                # "Têrêsa Calcutta Trần Di An"
                name = f"{saint_name} {last_name} {first_name}".replace("\xa0", "").strip()

                # if either name or số thứ tự (STT) is missing, skip this row
                if not name or not row[column_index].isdigit():
                    continue

                # Load background image
                background = Image.open(background_path)

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=8,
                    border=1,
                )

                # Add data to QR code: "Têrêsa Calcutta Trần Di An c1" or "Têrêsa Calcutta Trần Di An c1 06/08/2019"
                value = f"{name} {csv_filename} {note}".rstrip()
                qr.add_data(value)
                qr.make(fit=True)

                # Create QR code image
                qr_img = qr.make_image(fill_color="black", back_color="white")

                # Paste QR code image onto background
                background = create_and_position_qr(qr_img, background)

                # Add name text to the background
                draw = ImageDraw.Draw(background)
                draw_name_text(draw, background, saint_name, last_name, first_name, note)

                # Save the image (use the QR code value as filename)
                output_filename = f"{sanitize_filename(value)}.png"
                
                output_filepath = os.path.join(output_path, output_filename)
                background.save(output_filepath)

                print(f"✅ Generated card with QR for: {name}")
                qr_count += 1

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\n📍 Full traceback:")
        traceback.print_exc()
        
        # Get line number where error occurred
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            error_line = tb[-1].lineno
            error_file = tb[-1].filename
            print(f"\n� Error occurred at line {error_line} in {os.path.basename(error_file)}")
        
        sys.exit(1)

    print(
        f"\n🎉 Successfully generated {qr_count} ID cards with QR codes in '{output_path}/' directory!"
    )


if __name__ == "__main__":
    main()
