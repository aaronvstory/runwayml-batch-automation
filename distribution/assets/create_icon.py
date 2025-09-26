"""
Create a simple 'R' icon for the RunwayML Batch application
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 256x256 icon with R letter
def create_r_icon():
    # Create base image with gradient background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background with gradient effect
    # Purple to blue gradient background
    for i in range(size):
        color = (
            int(100 + (155 * i / size)),  # R: purple to blue
            int(50 + (100 * i / size)),    # G
            int(200 - (50 * i / size)),    # B
            255                             # A
        )
        draw.rectangle([i, 0, i+1, size], fill=color)

    # Draw rounded corners mask
    corner_radius = 40
    # Create a mask for rounded corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([10, 10, size-10, size-10], radius=corner_radius, fill=255)

    # Apply mask to create rounded corners
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)

    # Draw the letter "R" in white
    draw = ImageDraw.Draw(output)

    # Try to use a nice font, fall back to default if not available
    try:
        # Try Windows fonts
        font_size = 180
        font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 180)
        except:
            # Use default font as last resort
            font = ImageFont.load_default()

    # Draw the R letter
    text = "R"
    # Get text dimensions
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10  # Slight adjustment

    # Draw shadow
    draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0, 128))
    # Draw main text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    # Save multiple sizes for Windows ICO format
    output.save('icon_256.png')

    # Create smaller versions
    for ico_size in [16, 32, 48, 64, 128]:
        resized = output.resize((ico_size, ico_size), Image.Resampling.LANCZOS)
        resized.save(f'icon_{ico_size}.png')

    print("Icon images created successfully!")

    # Try to create ICO file
    try:
        # Create ICO with multiple sizes
        img_256 = Image.open('icon_256.png')
        img_128 = Image.open('icon_128.png')
        img_64 = Image.open('icon_64.png')
        img_48 = Image.open('icon_48.png')
        img_32 = Image.open('icon_32.png')
        img_16 = Image.open('icon_16.png')

        img_256.save('runway_icon.ico', format='ICO',
                    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("ICO file created successfully!")

        # Clean up temporary PNG files
        for ico_size in [16, 32, 48, 64, 128, 256]:
            os.remove(f'icon_{ico_size}.png')
        print("Temporary files cleaned up.")

    except Exception as e:
        print(f"Could not create ICO file: {e}")
        print("PNG files are available for manual conversion")

if __name__ == "__main__":
    create_r_icon()