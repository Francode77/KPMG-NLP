'''
Program expects Data/A/100/something.pdf structure
Create a "splitted" folder for the output and then run the program
This splits pdfs indiscriminately, it doesnt recognize if a file needs to be split or not
'''

import sys
import os
from alive_progress import alive_bar
from pdfminer.high_level import extract_text

directory = "Data"
from pdfrw import PdfReader, PdfWriter, PageMerge


def splitpage(src):
    ''' Split a page into two (left and right)
    '''
    # Yield a result for each half of the page
    for x_pos in (0, 0.5):
        yield PageMerge().add(src, viewrect=(x_pos, 0, 0.5, 1)).render()


# inpfn = sys.argv[1:]
# outfn = 'unspread.' + os.path.basename(inpfn)
split = 0
for dir in os.listdir(directory):
    print(dir)
    with alive_bar(len(os.listdir(f"{directory}/{dir}")),title="Splitting",bar="halloween") as bar:
        for pc in os.listdir(f"{directory}/{dir}"):
            for document in os.listdir(f"{directory}/{dir}/{pc}"):
                text = extract_text(f"{directory}/{dir}/{pc}/{document}")
                text = text.splitlines()
                if len(max(text,key=len)) < 60:
                    writer_NL = PdfWriter()
                    writer_FR = PdfWriter()
                    page_number = 0                        
                    for page in PdfReader(f"{directory}/{dir}/{pc}/{document}").pages:
                        page_number +=1
                        if page_number % 2 == 1:
                            print(page_number)
                            writer_NL.addpages(splitpage(page))
                        else:
                            writer_FR.addpages(splitpage(page))
                    writer_NL.write(f"splitted/NL_{document}")
                    writer_FR.write(f"splitted/FR_{document}")
                    split += 1
            bar()
print(f"Splitted pdfs: {split}")