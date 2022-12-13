'''
Program expects Data/A/100/something.pdf structure
Create a "splitted" folder for the output and then run the program
This splits pdfs indiscriminately, it doesnt recognize if a file needs to be split or not
'''

import sys
import os
from alive_progress import alive_bar

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

for dir in os.listdir(directory):
    print(dir)
    with alive_bar(len(os.listdir(f"{directory}/{dir}"))) as bar:
        for pc in os.listdir(f"{directory}/{dir}"):
            for document in os.listdir(f"{directory}/{dir}/{pc}"):
                writer = PdfWriter()                        
                for page in PdfReader(f"{directory}/{dir}/{pc}/{document}").pages:
                    writer.addpages(splitpage(page))
                writer.write(f"splitted/{document}")
            bar()