from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create a blank image
img = Image.new('RGB', (500, 300), color=(255, 255, 255))  # white background

# Set the fonts (you might need to change the path depending on where the font file is)
font_large = ImageFont.truetype("Arial.ttf", 40)
font_small = ImageFont.truetype("Arial.ttf", 25)

# Create a draw object
draw = ImageDraw.Draw(img)

# Define the "Cocaine" and ".Trade" parts of the title
cocaine_text = "Cocaine"
trade_text = ".Trade"

# Calculate width and height of each part of the title
cocaine_w, cocaine_h = font_large.getsize(cocaine_text)
trade_w, trade_h = font_large.getsize(trade_text)

# Calculate the total width and height of the title
title_w = cocaine_w + trade_w
title_h = max(cocaine_h, trade_h)

# Calculate the position of the title
title_x = (img.width - title_w) / 2
title_y = (img.height - title_h) / 2

# Draw the "Cocaine" part of the title in red
draw.text((title_x, title_y), cocaine_text, font=font_large, fill=(203, 32, 39))  # red text

# Draw the ".Trade" part of the title in blue
draw.text((title_x + cocaine_w, title_y), trade_text, font=font_large, fill=(75, 59, 151))  # blue text

# Draw the description in white
desc_text = "Latest firmware updates for Quest VR headsets"
desc_w, desc_h = font_small.getsize(desc_text)
desc_x = (img.width - desc_w) / 2
desc_y = title_y + title_h + 20
draw.text((desc_x, desc_y), desc_text, font=font_small, fill=(255, 255, 255))  # white text

# Create a background gradient
gradient = np.linspace(0, 1, img.height).reshape(-1, 1)  # vertical gradient from top to bottom
gradient = np.repeat(gradient, img.width, axis=1)
gradient = (gradient * 255).astype(np.uint8)
gradient_img = Image.fromarray(gradient)
img = Image.blend(img, gradient_img, alpha=0.3)

# Save the image
img.save('preview.png')
