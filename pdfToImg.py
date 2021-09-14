#!python3.9
import argparse
from os import makedirs, path

import fitz  # PyMuPDF

parser = argparse.ArgumentParser(description="Extracts images from pdf file")
parser.add_argument("input", nargs="?", default="a.pdf", help="Input file.")


def get_pages_as_img_list(pdf_filename):
    doc = fitz.open(pdf_filename)
    pixmaps = []
    for page in doc:
        pixmaps.append(page.getPixmap(alpha=False))  # render page to an image
    doc.close()
    return pixmaps


def write_pages(pixmaps, output_dir):
    for i, pixmap in enumerate(pixmaps):
        pixmap.writePNG(f"{output_dir}\\{i}.png")


if __name__ == "__main__":
    args = parser.parse_args()
    output_dir = path.basename(path.splitext(args.input)[0])
    makedirs(output_dir, exist_ok=True)
    pixmaps = get_pages_as_img_list(args.input)
    write_pages(pixmaps, output_dir)
