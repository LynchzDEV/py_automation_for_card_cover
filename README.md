# Collage Creator

A Python script that processes images (e.g., .png, .jpg, .jpeg) by **extending** the edges with a bottom-based color and optionally a white border, then arranges them into a **90×90 cm** collage. Finally, it exports the collage in one of several formats: **PNG**, **PDF**, **SVG**, or **AI**.

## Features

1. **Edge Extension**
   - Detects either the most common color or the average color from the **bottom strip** of each image.
   - Extends the top/bottom/left/right edges with that color.

2. **White Border** (optional)
   - Adds a uniform white border around each extended image (if `WHITE_BORDER_CM` > 0).

3. **Resizing**
   - Resizes each processed image to a **final design size** before composing them into a collage.

4. **Collage Composition**
   - Places images in a **15×10 grid** on a **90×90 cm** canvas, using `ImageOps.fit` so each cell is fully covered (images may be cropped slightly).

5. **Multiple Output Formats**
   - Exports collages as **PNG** by default.
   - Supports exporting **PDF** (single page), **SVG** (raster image embedded in SVG), and **AI** (EPS fallback with `.ai` extension).

## Requirements

- **Python 3.7+** (or later)
- **Pillow (PIL)** library for image processing
- **argparse** (usually included with Python by default)
- Basic understanding of the command line if using CLI arguments

Install Pillow (if not already installed):

```bash
pip install Pillow
```

## Usage

1. **Place source images** in an `images` folder. Files must have extensions `.png`, `.jpg`, or `.jpeg`.
2. **Run the script** from the terminal or command prompt.

### Command-Line Arguments

You can specify the output format with the `--format` argument:

```bash
python collage_script.py --format [png|pdf|svg|ai]
```

- **png** (default) – Exports each collage as `.png` files.
- **pdf** – Creates a single-page PDF containing the collage (raster at 300 DPI).
- **svg** – Embeds a raster image (PNG) inside an SVG wrapper. *Not vectorized.*
- **ai** – Saves as EPS data with a `.ai` extension (raster embedded in PostScript/EPS). *Not true Illustrator vector.*

If you omit `--format`, **PNG** is used by default.

### Example Commands

- **Default to PNG**:
  ```bash
  python collage_script.py
  ```
- **Export as PDF**:
  ```bash
  python collage_script.py --format pdf
  ```
- **Export as SVG**:
  ```bash
  python collage_script.py --format svg
  ```

### Output Files

- Collages are saved in an `output` folder, created automatically if it doesn’t exist.
- File names follow the pattern:
  ```
  final_canvas_0.png   (or .pdf / .svg / .ai)
  final_canvas_1.png   (or .pdf / .svg / .ai)
  ...
  ```
  Each file corresponds to a batch of up to 150 images (15 columns × 10 rows).

## Customization

Open the script (`collage_script.py`) and modify the **GLOBAL CONSTANTS** to your needs:

- **`AVERAGE_COLOR`** – Switch between average color vs. most common color from the bottom strip.
- **Canvas Dimensions** (`CANVAS_CM`) – Adjust the collage size in centimeters.
- **Rows/Columns** (`COLUMNS`, `ROWS`) – Change how many images fit on one collage.
- **Extend Amounts** (`EXTEND_TOP_BOTTOM`, `EXTEND_LEFT_RIGHT`) – Adjust the added edge thickness in pixels.
- **White Border** (`WHITE_BORDER_CM`) – Set to `0.00` if you don’t want a white border.
- **Image Size** (`IMAGE_WIDTH_CM`, `IMAGE_HEIGHT_CM`) – Change the target image dimension.

## Notes on Formats

1. **PNG** – High-quality raster format.
2. **PDF** – Raster data embedded in a single-page PDF.
3. **SVG** – Contains a `<image>` tag with base64-encoded PNG data. **Not** truly vector.
4. **AI** – Actually an EPS fallback; modern Illustrator can open/edit this file, but it is still raster data inside.

If you require **true vector** graphics, you would need to reconstruct shapes, text, or other vector elements via a different approach. Simply embedding photos always involves raster data.

## Troubleshooting

- **White Edges or Cropping**: `ImageOps.fit` will crop images if their aspect ratio differs from the collage cell size. If you want no cropping at all, replace `ImageOps.fit` with `ImageOps.contain` (though it will leave blank space).
- **Memory Errors**: Processing very large images or hundreds of files can be memory-intensive. You may need more RAM or reduce the canvas size.
- **SVG or AI not truly scalable**: As noted, the script rasterizes images in these formats. This is expected behavior when dealing with photos.

## Contact

For any questions, please reach out to:
- [Lynchz](https://github.com/LynchzDEV)
