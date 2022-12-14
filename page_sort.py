import os
from pdfrw import PdfReader, PdfWriter
from alive_progress import alive_bar

path = "split"

try:
    os.mkdir("Nederlands")
except:
    pass

try:
    os.mkdir("Francais")
except:
    pass

with alive_bar(len(os.listdir(path))) as bar:
    for document in os.listdir(path):
        writer_NL = PdfWriter()
        writer_FR = PdfWriter()
        page_number = 0
        for page in PdfReader(f"{path}/{document}").pages:
            page_number += 1
            if page_number%2 == 1:
                writer_NL.addpage(page)
            else:
                writer_FR.addpage(page)
        writer_NL.write(f"Nederlands/NL_{document}")
        writer_FR.write(f"Francais/FR_{document}")
        bar()