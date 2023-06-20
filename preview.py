from PIL import Image, ImageDraw, ImageFont

SCALE_FACTOR = 8
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 630

def calculate_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def calculate_text_position(img, text_width, text_height):
    return (img.width - text_width) // 2, (img.height - text_height) // 2

def get_fonts():
    font_large = ImageFont.truetype("unifont-13.0.06.ttf", 110 * SCALE_FACTOR)
    font_small = ImageFont.truetype("unifont-13.0.06.ttf", 44 * SCALE_FACTOR)
    return font_large, font_small

def main():
    img = Image.new('RGB', (IMAGE_WIDTH * SCALE_FACTOR, IMAGE_HEIGHT * SCALE_FACTOR), color=(0, 0, 0))
    font_large, font_small = get_fonts()
    draw = ImageDraw.Draw(img)

    cocaine_text = "Cocaine"
    trade_text = ".Trade"
    desc_text = "Firmware archive for Quest VR headsets"

    # Calculate the total height of the title and the description
    title_size = calculate_text_size(draw, cocaine_text + trade_text, font_large)
    desc_size = calculate_text_size(draw, desc_text, font_small)
    total_height = title_size[1] + 20 * SCALE_FACTOR + desc_size[1]

    # Calculate the position of the title so that the entire text block is centered
    title_position = ((img.width - title_size[0]) // 2, (img.height - total_height) // 2)

    draw.text(title_position, cocaine_text, font=font_large, fill=(203, 32, 39))  # red text
    draw.text((title_position[0] + calculate_text_size(draw, cocaine_text, font_large)[0], title_position[1]), trade_text, font=font_large, fill=(75, 59, 151))  # blue text

    desc_position = (calculate_text_position(img, *desc_size)[0], title_position[1] + title_size[1] + 20 * SCALE_FACTOR)
    draw.text(desc_position, desc_text, font=font_small, fill=(255, 255, 255))  # white text

    img = img.resize((img.width // SCALE_FACTOR, img.height // SCALE_FACTOR), Image.NEAREST)
    img.save('preview.png')

if __name__ == "__main__":
    main()
