import os
from PIL import Image, ImageOps
from collections import Counter

#-------------------------#
# GLOBAL CONSTANTS #
#-------------------------#

DPI = 300
CM_TO_PX = lambda cm: round(cm * (DPI / 2.54))

CANVAS_CM = 90
CANVAS_SIZE = CM_TO_PX(CANVAS_CM)
COLUMNS = 15
ROWS = 10

CELL_WIDTH = CANVAS_SIZE // COLUMNS
CELL_HEIGHT = CANVAS_SIZE // ROWS

IMAGE_WIDTH_CM = 5.4
IMAGE_HEIGHT_CM = 8.56
EXTEND_COLOR_CM = 0.15
WHITE_BORDER_CM = 0.00

BASE_IMAGE_WIDTH_PX = CM_TO_PX(IMAGE_WIDTH_CM)
BASE_IMAGE_HEIGHT_PX = CM_TO_PX(IMAGE_HEIGHT_CM)
EXTEND_COLOR_PX = CM_TO_PX(EXTEND_COLOR_CM)
WHITE_BORDER_PX = CM_TO_PX(WHITE_BORDER_CM)

DESIGN_FINAL_WIDTH_PX = BASE_IMAGE_WIDTH_PX + 2 * (EXTEND_COLOR_PX + WHITE_BORDER_PX)
DESIGN_FINAL_HEIGHT_PX = BASE_IMAGE_HEIGHT_PX + 2 * (EXTEND_COLOR_PX + WHITE_BORDER_PX)

OUTPUT_FORMAT = "png"  # Options: "png", "pdf", "svg"

#-------------------------#
#  IMAGE PROCESSING STEP  #
#-------------------------#

def get_primary_color(image):
    """
    Get the most common color in the image excluding white.
    """
    image = image.convert('RGB')
    pixels = list(image.getdata())
    non_white_pixels = [pixel for pixel in pixels if pixel != (255, 255, 255)]
    most_common_color = Counter(non_white_pixels).most_common(1)[0][0]
    return most_common_color

def process_image(file_path):
    """
    Process an image by extending edges, adding a white border,
    and resizing it to the design dimension.
    """
    # Open the image
    image = Image.open(file_path)

    # Step 1: Extend edges with the background color
    primary_color = get_primary_color(image)
    total_pixels = image.width * image.height
    white_pixels = sum(1 for pixel in image.getdata() if pixel == (255, 255, 255))

    if white_pixels / total_pixels > 0.8:
        primary_color = (255, 255, 255)

    extended_image = ImageOps.expand(image, border=EXTEND_COLOR_PX, fill=primary_color[0])

    # Step 2: Add a white border
    final_image = ImageOps.expand(extended_image, border=WHITE_BORDER_PX, fill=255)

    # Step 3: Resize to the design final dimension
    resized = final_image.resize((DESIGN_FINAL_WIDTH_PX, DESIGN_FINAL_HEIGHT_PX), Image.Resampling.LANCZOS)

    return resized

#-------------------------#
#  FINAL COLLAGE CREATION #
#-------------------------#

def create_collage(processed_images, canvas_index):
    """
    Arrange processed images on a 90x90 cm canvas in a grid.
    """
    if OUTPUT_FORMAT in ["png", "pdf"]:
        # Create a blank canvas
        canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))

        for i, img in enumerate(processed_images):
            row = i // COLUMNS
            col = i % COLUMNS

            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT

            # Resize image to fit the cell size
            img = ImageOps.contain(img, (CELL_WIDTH, CELL_HEIGHT))

            # Paste the image onto the canvas
            canvas.paste(img, (x, y))

        # Save the final canvas
        output_path = os.path.join("output", f"final_canvas_{canvas_index}.{OUTPUT_FORMAT}")
        os.makedirs("output", exist_ok=True)
        if OUTPUT_FORMAT == "png":
            canvas.save(output_path)
        elif OUTPUT_FORMAT == "pdf":
            canvas.save(output_path, "PDF", resolution=DPI)
        print(f"Collage created successfully at {output_path}.")

    # elif OUTPUT_FORMAT == "svg":
    #     dwg = svgwrite.Drawing(os.path.join("output", f"final_canvas_{canvas_index}.svg"), size=(CANVAS_SIZE, CANVAS_SIZE))
    #     for i, img in enumerate(processed_images):
    #         row = i // COLUMNS
    #         col = i % COLUMNS

    #         x = col * CELL_WIDTH
    #         y = row * CELL_HEIGHT

    #         # Resize image to fit the cell size
    #         img = ImageOps.contain(img, (CELL_WIDTH, CELL_HEIGHT))
    #         img_path = os.path.join("output", f"temp_image_{i}.png")
    #         img.save(img_path)

    #         # Add image to SVG
    #         dwg.add(dwg.image(img_path, insert=(x, y), size=(CELL_WIDTH, CELL_HEIGHT)))

    #     dwg.save()
    #     print(f"Collage created successfully at {os.path.join('output', f'final_canvas_{canvas_index}.svg')}.")

#-------------------------#
#         MAIN APP        #
#-------------------------#

def main():
    try:
        input_dir = "images"
        output_dir = "output"

        os.makedirs(output_dir, exist_ok=True)

        # Gather all .png/.jpg/.jpeg files
        files = [
            os.path.join(input_dir, file)
            for file in os.listdir(input_dir)
            if file.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        # Process each image
        processed_images = [process_image(file) for file in files]

        # Create and save the final collage(s)
        max_images_per_canvas = COLUMNS * ROWS
        for i in range(0, len(processed_images), max_images_per_canvas):
            create_collage(processed_images[i:i + max_images_per_canvas], i // max_images_per_canvas)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
