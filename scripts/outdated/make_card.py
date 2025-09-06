from PIL import Image

# Load the images
background = Image.open("background.png")  # Replace with your background image
foreground = Image.open("pic2.png")  # Replace with your smaller image

# Ensure the foreground image has an alpha channel
if foreground.mode != "RGBA":
    foreground = foreground.convert("RGBA")

# Resize the foreground image (set desired width and height)
new_size = (100, 100)  # Change to desired size
foreground = foreground.resize(new_size, Image.LANCZOS)

# Set the position where you want to paste the smaller image (x, y)
position = (50, 50)  # Adjust as needed

# Paste the foreground onto the background
background.paste(
    foreground, position, foreground.split()[3]
)  # Use the alpha channel as the mask

# Save or show the final image
background.save("output.jpg")  # Change format as needed
background.show()
