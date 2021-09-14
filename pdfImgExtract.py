#!python3.9
import argparse
from os import makedirs, path

import fitz  # PyMuPDF

parser = argparse.ArgumentParser(description="Extracts images from pdf file")
parser.add_argument("input", nargs="?", default="a.pdf", help="Input file.")


def get_pixmaps_in_pdf(pdf_filename):
    doc = fitz.open(pdf_filename)
    xrefs = set()
    for page_index in range(doc.pageCount):
        for image in doc.getPageImageList(page_index):
            xrefs.add(image[0])  # Add XREFs to set so duplicates are ignored
    pixmaps = [fitz.Pixmap(doc, xref) for xref in xrefs]
    doc.close()
    return pixmaps


def write_pixmaps_to_pngs(pixmaps, output_dir):
    for i, pixmap in enumerate(pixmaps):
        pixmap.writePNG(f"{output_dir}\\{i}.png")


if __name__ == "__main__":
    args = parser.parse_args()
    output_dir = path.basename(path.splitext(args.input)[0])
    makedirs(output_dir, exist_ok=True)
    pixmaps = get_pixmaps_in_pdf(args.input)
    write_pixmaps_to_pngs(pixmaps, output_dir)
