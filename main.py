import os
import sys
import argparse
from PIL import Image, ImageOps
from collections import Counter

# ------------------------- #
# GLOBAL CONSTANTS          #
# ------------------------- #

AVERAGE_COLOR = False

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

EXTEND_TOP_BOTTOM = 30
EXTEND_LEFT_RIGHT = 15

BASE_IMAGE_WIDTH_PX = CM_TO_PX(IMAGE_WIDTH_CM)
BASE_IMAGE_HEIGHT_PX = CM_TO_PX(IMAGE_HEIGHT_CM)
EXTEND_COLOR_PX = CM_TO_PX(EXTEND_COLOR_CM)
WHITE_BORDER_PX = CM_TO_PX(WHITE_BORDER_CM)

DESIGN_FINAL_WIDTH_PX = (
    BASE_IMAGE_WIDTH_PX + 2 * (EXTEND_COLOR_PX + WHITE_BORDER_PX)
)
DESIGN_FINAL_HEIGHT_PX = (
    BASE_IMAGE_HEIGHT_PX + 2 * (EXTEND_COLOR_PX + WHITE_BORDER_PX)
)


# ------------------------- #
# HELPER: GET BOTTOM AVG    #
# ------------------------- #

def get_bottom_average_color(image, strip_height=1):
    """
    Return the average color (R, G, B) of the bottom strip
    of `strip_height` pixels.
    """
    image = image.convert('RGB')
    bottom_strip = image.crop(
        (0, image.height - strip_height, image.width, image.height)
    )
    pixels = list(bottom_strip.getdata())

    num_pixels = len(pixels)
    if num_pixels == 0:
        return (255, 255, 255)  # fallback

    sum_r = sum(p[0] for p in pixels)
    sum_g = sum(p[1] for p in pixels)
    sum_b = sum(p[2] for p in pixels)

    avg_r = sum_r // num_pixels
    avg_g = sum_g // num_pixels
    avg_b = sum_b // num_pixels

    return (avg_r, avg_g, avg_b)


def get_bottom_color(image, strip_height=1):
    """
    Return the most common color in the bottom strip (height = strip_height pixels).
    If it turns out to be all white, default to white.
    """
    image = image.convert('RGB')

    bottom_strip = image.crop(
        (0, image.height - strip_height, image.width, image.height)
    )
    pixels = list(bottom_strip.getdata())

    non_white_pixels = [p for p in pixels if p != (255, 255, 255)]
    if non_white_pixels:
        most_common_color = Counter(non_white_pixels).most_common(1)[0][0]
    else:
        most_common_color = (255, 255, 255)

    return most_common_color


# ------------------------- #
#  IMAGE PROCESSING STEP    #
# ------------------------- #

def process_image(file_path):
    """
    Process each image by extending top/bottom + left/right with
    a color based on the bottom strip of the original image.
    Then optionally add a white border, then resize.
    """
    image = Image.open(file_path)

    # Choose either average color or most common color:
    if AVERAGE_COLOR:
        bottom_avg_color = get_bottom_average_color(image, strip_height=5)
    else:
        bottom_avg_color = get_bottom_color(image, strip_height=5)

    extended_image = ImageOps.expand(
        image,
        border=(EXTEND_LEFT_RIGHT, EXTEND_TOP_BOTTOM, EXTEND_LEFT_RIGHT, EXTEND_TOP_BOTTOM),
        fill=bottom_avg_color
    )

    if WHITE_BORDER_PX > 0:
        extended_image = ImageOps.expand(extended_image, border=WHITE_BORDER_PX, fill='white')

    # Resize to final dimension
    # (If you use ImageOps.fit here, it may crop. We'll do a simple resize.)
    resized = extended_image.resize(
        (DESIGN_FINAL_WIDTH_PX, DESIGN_FINAL_HEIGHT_PX),
        Image.Resampling.LANCZOS
    )
    return resized


# ------------------------- #
#  FINAL COLLAGE CREATION   #
# ------------------------- #

def create_collage(processed_images, canvas_index, output_format):
    """
    Arrange processed images on a 90x90 cm canvas in a grid.
    Then export based on the chosen output_format.
    """
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))

    for i, img in enumerate(processed_images):
        row = i // COLUMNS
        col = i % COLUMNS
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT

        # Fill the cell entirely by cropping if needed
        fitted_img = ImageOps.fit(
            img,
            (CELL_WIDTH, CELL_HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )
        canvas.paste(fitted_img, (x, y))

    # Determine output path based on format
    base_name = f"final_canvas_{canvas_index}"
    if output_format == "png":
        out_path = os.path.join("output", base_name + ".png")
        canvas.save(out_path, "PNG")
    elif output_format == "pdf":
        out_path = os.path.join("output", base_name + ".pdf")
        canvas.save(out_path, "PDF", resolution=300)
    elif output_format == "svg":
        png_path = os.path.join("output", base_name + "_temp.png")
        canvas.save(png_path, "PNG")

        svg_path = os.path.join("output", base_name + ".svg")
        embed_png_in_svg(png_path, svg_path, canvas.width, canvas.height)

        os.remove(png_path)
        out_path = svg_path
    elif output_format == "ai":
        out_path = os.path.join("output", base_name + ".eps")
        canvas.save(out_path, "EPS")
    else:
        # Default fallback
        out_path = os.path.join("output", base_name + ".png")
        canvas.save(out_path, "PNG")

    print(f"Collage created successfully at {out_path}.")


def embed_png_in_svg(png_path, svg_path, width_px, height_px):
    """
    Minimal function to embed a PNG in an SVG.
    This is not a true vector conversion — just a raster data embed.
    """
    import base64

    with open(png_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    # For a 300 DPI image, 1 inch = 300 px. If you want real size in mm/cm,
    # you'd do some calculations. We'll just put the same px as the <svg width/height>.
    svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width_px}"
    height="{height_px}"
    version="1.1">
  <image href="data:image/png;base64,{encoded}"
         x="0" y="0"
         width="{width_px}"
         height="{height_px}" />
</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as svg_file:
        svg_file.write(svg_content)


# ------------------------- #
#         MAIN APP          #
# ------------------------- #

def parse_args():
    parser = argparse.ArgumentParser(description="Create collage and export in various formats.")
    parser.add_argument(
        "--format",
        choices=["png", "pdf", "svg", "ai"],
        default="png",
        help="Output format (png, pdf, svg, ai). Default is png."
    )
    return parser.parse_args()

def main():
    try:
        args = parse_args()
        output_format = args.format

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
            create_collage(
                processed_images[i:i + max_images_per_canvas],
                i // max_images_per_canvas,
                output_format
            )

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
