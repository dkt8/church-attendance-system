import os

from PIL import Image, ImageDraw, ImageFont


def overlay_images(
    target, name, overlay_path, saint_name, full_name, x_position, y_position
):
    os.makedirs(target + "_card", exist_ok=True)

    # Open the background and overlay images
    background = Image.open("background_" + target + ".png")
    overlay = Image.open(overlay_path)
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font_size = 50

    # Convert images to RGBA if they aren't already
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    # Create a new image with the same size as background
    result = Image.new("RGBA", background.size)

    # Paste the background first
    result.paste(background, (0, 0))

    # Paste the overlay in a fixed position
    result.paste(overlay, (125, 255), overlay)

    # Add text to the image
    draw = ImageDraw.Draw(result)
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("arial.ttf", font_size)  # Use Arial as a fallback
    except:
        font = ImageFont.load_default()

    # Measure text width & height
    text_bbox = draw.textbbox((0, 0), saint_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Adjust X and Y positions to center the text relative to input positions
    x_adjusted = x_position - (text_width // 2)
    y_adjusted = y_position - (text_height // 2)

    # Draw text with manually assigned and centered positions
    draw.text(
        (x_adjusted, y_adjusted), saint_name, font=font, fill=(0, 0, 0, 255)
    )  # Black text with full opacity

    # Measure text width & height
    text_bbox = draw.textbbox((0, 0), full_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Adjust X and Y positions to center the text relative to input positions
    x_adjusted = x_position - (text_width // 2)
    y_adjusted = y_position - (text_height // 2)
    if x_adjusted + text_width > background.width:
        font = ImageFont.truetype(font_path, font_size * 0.8)

        text_bbox = draw.textbbox((0, 0), full_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Adjust X and Y positions to center the text relative to input positions
        x_adjusted = x_position - (text_width // 2)
        y_adjusted = y_position - (text_height // 2)
        draw.text(
            (x_adjusted, y_adjusted + 100), full_name, font=font, fill=(0, 0, 0, 255)
        )  # Black text with full opacity
    else:
        draw.text(
            (x_adjusted, y_adjusted + 100), full_name, font=font, fill=(0, 0, 0, 255)
        )  # Black text with full opacity

    # Save the result
    result.resize((340, 227)).save(os.path.join(target + "_card", name))
    # result.save(output_path, 'PNG')
    # result.save(os.path.join("card", name))


# if __name__ == "__main__":
# Example usage
# background_path = "background.png"
# overlay_path = "pic2.png"
# text = "123456789 0 987654321"
# x_position = 800  # Assign custom X position
# y_position = 300  # Assign custom Y position
# font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
# font_size = 50
# name = "myresult.png"
# overlay_images(
#     name, overlay_path, text, x_position, y_position)
