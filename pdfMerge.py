import sys

from PyPDF2 import PdfFileMerger


def pdf_merge(pdfs, output):
    merger = PdfFileMerger(strict=False)
    for pdf in pdfs:
        merger.append(pdf)
    with open(output, "wb") as fout:
        merger.write(fout)
    merger.close()


if __name__ == "__main__":
    pdf_merge(sys.argv[1:], f"merged_{len(sys.argv)-1}.pdf")
