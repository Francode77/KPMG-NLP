import sys
import os
from os import listdir
import pandas as pd
from statistics import mean,median
from pdfminer.high_level import extract_text
from pdfrw import PdfReader, PdfWriter, PageMerge


def splitpage(src):
        """Split a page into two (left and right)"""
        # Yield a result for each half of the page
        for x_pos in (0, 0.5):
            yield PageMerge().add(src, viewrect=(x_pos, 0, 0.5, 1)).render()

def split_file(path,document,language):
    
    out_path=os.path.join('..','tmp','pdf')  

    
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    document=f'{document}.pdf'
    text = extract_text(os.path.join(path,document))
 
    x=[] 
    for i in text.splitlines():

        # Filter out table data
        if (len(i)>40):

            x.append(len(i))

    # Calculate the average length of sentences outside tables
    res_mean=mean(x)
    res_median=median(x)
    text = text.splitlines()
    
    if len(max(text, key=len)) <=67 or len(max(text, key=len)) >67 and res_mean <55 and res_median<55:
        
        writer = PdfWriter()
        page_number = 0
        for page in PdfReader(os.path.join(path,document)).pages:
            writer.addpages(splitpage(page))

        writer.write(os.path.join(out_path,document))

        writer_NL = PdfWriter()
        writer_FR = PdfWriter()

        page_number = 0 
        for page in PdfReader(os.path.join(out_path,document)).pages: 
            page_number += 1
            if page_number%2 == 1:
                writer_NL.addpage(page)
            else:
                writer_FR.addpage(page)

        if language == 'NL':
            writer_NL.write(os.path.join(out_path,document))
        
        if language == 'FR':
            writer_FR.write(os.path.join(out_path,document))

        status_code="Success"
        return status_code

    return 'FAIL'