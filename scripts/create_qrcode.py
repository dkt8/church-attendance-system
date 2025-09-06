import csv
import os
import sys
from pathlib import Path

import qrcode


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
                    # Generate QR code
                    qr = qrcode.make(f"{name} {csv_filename}")
                    qr_filename = f"{name} {csv_filename}.png"
                    qr_filepath = os.path.join(output_path, qr_filename)
                    qr.save(qr_filepath)

                    print(f"✅ Generated QR for: {qr_filename}")
                    qr_count += 1

    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        sys.exit(1)

    print(
        f"\n🎉 Successfully generated {qr_count} QR codes in '{output_path}/' directory!"
    )


if __name__ == "__main__":
    main()
