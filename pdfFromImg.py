from glob import glob
from sys import argv

from fpdf import FPDF
from PIL import Image


def makePdf(pdfFileName, listPages):

    cover = Image.open(listPages[0])
    width, height = cover.size

    pdf = FPDF(unit="pt", format=[width, height])

    for page in listPages:
        pdf.add_page()
        pdf.image(page, 0, 0)

    pdf.output(pdfFileName, "F")


if __name__ == "__main__":
    imglist = []
    if len(argv) > 1:
        ftype = argv[1]
    else:
        ftype = "jpg"
    for img in glob(f"*.{ftype}"):
        imglist.append(img)
    makePdf("imgmerge.pdf", imglist)
