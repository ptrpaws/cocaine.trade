from PIL import Image, ImageDraw, ImageFont

# Create a blank image
img = Image.new('RGB', (500, 300), color=(0, 0, 0))  # black background

# Set the fonts (you might need to change the path depending on where the font file is)
font_large = ImageFont.truetype("unifont-13.0.06.ttf", 30)
font_small = ImageFont.truetype("unifont-13.0.06.ttf", 20)

# Create a draw object
draw = ImageDraw.Draw(img)

# Define the "Cocaine" and ".Trade" parts of the title
cocaine_text = "Cocaine"
trade_text = ".Trade"

# Calculate width and height of each part of the title
cocaine_w, cocaine_h = font_large.getbbox(cocaine_text)[2:]
trade_w, trade_h = font_large.getbbox(trade_text)[2:]

# Calculate the total width and height of the title
title_w = cocaine_w + trade_w
title_h = max(cocaine_h, trade_h)

# Draw the "Cocaine" part of the title in red
draw.text(((img.width - title_w) / 2, (img.height - title_h) / 2), cocaine_text, font=font_large, fill=(203, 32, 39))  # red text

# Draw the ".Trade" part of the title in blue
draw.text((((img.width - title_w) / 2) + cocaine_w, (img.height - title_h) / 2), trade_text, font=font_large, fill=(75, 59, 151))  # blue text

# Draw the description in white
desc_text = "Latest firmware updates for Quest VR headsets"
desc_w, desc_h = font_small.getbbox(desc_text)[2:]
draw.text(((img.width - desc_w) / 2, ((img.height - desc_h) / 2) + title_h), desc_text, font=font_small, fill=(255, 255, 255))  # white text

# Save the image
img.save('preview.webp')
