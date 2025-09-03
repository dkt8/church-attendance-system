import csv
import os
import sys
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont


def draw_name_text(draw, row, font, text_x, text_y):
    """
    Draw student name text on ID card with intelligent line wrapping.
    
    Args:
        draw (ImageDraw.Draw): PIL ImageDraw object for drawing on image
        row (list): CSV row containing [number, saint_name, first_name, last_name]
        font (ImageFont): PIL font object for text rendering
        text_x (int): Horizontal center position for text placement
        text_y (int): Vertical center position for text block
    
    Line Breaking Rules:
        - Saint name (row[1]): Wrapped at 12 characters with word boundaries
        - Remaining name (row[2] + row[3]): Wrapped at 12 characters with word boundaries
        - All lines are centered horizontally at text_x position
        - 60-pixel spacing between lines
        - Text color: black, anchor: "ma" (middle-ascender)
    
    Example:
        "Têrêsa Calcutta Trần Di An" becomes:
        Line 1: "Têrêsa"
        Line 2: "Calcutta" 
        Line 3: "Trần Di An"
    """
    lines = []
    saint_name = row[1].strip()
    remaining = f"{row[2]} {row[3]}".strip()
    
    # Apply 12-char line breaking to saint name
    if len(saint_name) <= 12:
        lines.append(saint_name)
    else:
        words = saint_name.split()
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if len(test) <= 12:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    
    # Apply 12-char line breaking to remaining name
    if len(remaining) <= 12:
        lines.append(remaining)
    else:
        words = remaining.split()
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if len(test) <= 12:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    
    # Draw centered text block
    line_spacing = 60
    start_y = text_y - ((len(lines) - 1) * line_spacing // 2)
    
    for i, line in enumerate(lines):
        draw.text((text_x, start_y + i * line_spacing), line, 
                 font=font, fill="black", anchor="ma")


def main():
    # Check if CSV file path is provided
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 create_qrcode.py <csv_input_path> [output_path]")
        print("Example: python3 create_qrcode.py data/csv_files/au1.csv")
        print(
            "Example: python3 create_qrcode.py data/csv_files/au1.csv output/au1_qrcodes"
        )
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
                # only process student record (e.g. 1 ,Têrêsa Calcutta, Trần Di An)
                if not row[0].isdigit():
                    continue

                # Build the full name from columns 1, 2, 3 (assuming saint name, first name, last name)
                name = f"{row[1]} {row[2]} {row[3]}".replace("\xa0", "").strip()

                if name:  # Check if the name is not empty
                    # Load background image
                    background = Image.open(background_path)
                    
                    # Generate QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=8,
                        border=1,
                    )
                    qr.add_data(f"{name} {csv_filename}")
                    qr.make(fit=True)
                    
                    # Create QR code image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Resize QR code to fit nicely on card (adjust size as needed)
                    qr_size = 450  # pixels
                    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
                    
                    # Calculate position based on percentage from edges
                    bg_width, bg_height = background.size
                    
                    # Simple positioning settings (adjust these percentages)
                    horizontal_percent = 32  # % from left edge (0% = left, 100% = right)
                    vertical_percent = 60    # % from top edge (0% = top, 100% = bottom)
                    
                    # Calculate QR position (center the QR at the percentage point)
                    qr_x = int(bg_width * horizontal_percent / 100) - (qr_size // 2)
                    qr_y = int(bg_height * vertical_percent / 100) - (qr_size // 2)
                    
                    # === Paste QR code onto background ===
                    background.paste(qr_img, (qr_x, qr_y))
                    
                    # Add name text to the background
                    draw = ImageDraw.Draw(background)
                    
                    # Text positioning settings (adjust these percentages)
                    text_horizontal_percent = 77  # % from left edge (centered)
                    text_vertical_percent = 50    # % from top edge
                    
                    # Calculate text position
                    text_x = int(bg_width * text_horizontal_percent / 100)
                    text_y = int(bg_height * text_vertical_percent / 100)
                    
                    # Modern bold font - great for readability
                    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
                    # font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 60)
                    # font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
      
                    
                    # === Draw name text ===
                    draw_name_text(draw, row, font, text_x, text_y)
                    
                    # Save the combined image
                    output_filename = f"{name} {csv_filename}.png"
                    output_filepath = os.path.join(output_path, output_filename)
                    background.save(output_filepath)

                    print(f"✅ Generated card with QR for: {name}")
                    qr_count += 1

    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        sys.exit(1)

    print(
        f"\n🎉 Successfully generated {qr_count} ID cards with QR codes in '{output_path}/' directory!"
    )


if __name__ == "__main__":
    main()
