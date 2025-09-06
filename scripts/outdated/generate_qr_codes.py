#!/usr/bin/env python3
"""
Main script for generating QR codes and ID cards from CSV data
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from image_processing.overlay_images import create_id_cards
from qr_generation.create_qrcode import generate_qr_codes_from_csv


def load_config():
    """Load configuration from settings.json"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate QR codes and ID cards for attendance system"
    )
    parser.add_argument("csv_file", help="Path to CSV file containing student data")
    parser.add_argument("--output-dir", help="Output directory for generated files")
    parser.add_argument(
        "--create-cards", action="store_true", help="Also create ID cards with QR codes"
    )
    parser.add_argument("--config", help="Path to configuration file")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = load_config()

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Extract group name from CSV filename
        csv_name = Path(args.csv_file).stem
        output_dir = f"output/{csv_name}"

    # Check if CSV file exists
    if not Path(args.csv_file).exists():
        print(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)

    print(f"📄 Processing: {args.csv_file}")
    print(f"📁 Output directory: {output_dir}")

    # Generate QR codes
    try:
        qr_count = generate_qr_codes_from_csv(args.csv_file, output_dir, config)
        print(f"✅ Generated {qr_count} QR codes")

        if args.create_cards:
            card_count = create_id_cards(args.csv_file, output_dir, config)
            print(f"✅ Generated {card_count} ID cards")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

    print("🎉 Generation completed successfully!")


if __name__ == "__main__":
    main()
