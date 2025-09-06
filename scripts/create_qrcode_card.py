import csv
import os
import sys
from pathlib import Path

import qrcode
from PIL import Image


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
                    horizontal_percent = (
                        32  # % from left edge (0% = left, 100% = right)
                    )
                    vertical_percent = 60  # % from top edge (0% = top, 100% = bottom)

                    # Calculate QR position (center the QR at the percentage point)
                    qr_x = int(bg_width * horizontal_percent / 100) - (qr_size // 2)
                    qr_y = int(bg_height * vertical_percent / 100) - (qr_size // 2)

                    # Paste QR code onto background
                    background.paste(qr_img, (qr_x, qr_y))

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
