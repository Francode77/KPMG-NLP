
# This file contains the functions to be called from the app
# Everything is done by process_pdf()

# Google DocumentAI parameters
project_id = ''
location = 'eu'  
processor_display_name = 'PDF_PROCESSOR_EU' 
processor_type = 'OCR_PROCESSOR'  
processor_version = 'rc' 
mime_type = 'application/pdf' 
processor_id = ''

# Imports
import os
import re
import pandas as pd
import shutil
from os import listdir 
import os
import fasttext as ft 
import PyPDF2
from typing import Sequence
from google.api_core.client_options import ClientOptions
from google.cloud import documentai


# FASTTEXT LANGUAGE detection 
ft_model = ft.load_model(os.path.join('..','preprocessing',"lid.176.ftz"))
def fasttext_language_predict(text, model = ft_model): 
  text = text.replace('\n', " ")
  prediction = model.predict([text]) 
  return prediction

# PROCESS DOCUMENT AI CORE
# This function links Document AI from Google to the Google processor 
def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    
    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor version
    # e.g. projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}
    # You must create processors before running sample code.
    name = client.processor_version_path(
        project_id, location, processor_id, processor_version
    )

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    result = client.process_document(request=request)
    return result.document

# OCR Processing
# Function to process document with Google Cloud
def process_document_ocr(    project_id: str,    location: str,    processor_id: str,
    processor_version: str,    file_path: str,    document_id: str,    mime_type: str, output_path) -> None:

    # Online processing request to Document AI
    document = process_document(project_id, location, processor_id, processor_version, file_path, mime_type)
    text = document.text 
    
    # Clean the filename
    document_id_filename=re.sub('.pdf','',document_id)
    
    # Write document as text file
    with open(f'{output_path}/{document_id_filename}.txt', 'w', encoding="utf-8") as f:
        f.write(text) 
    # make new_row
    cols=[] 
    new_row=[document_id]
    cols.append('document_id')

    # detect if pdf has multiple parts (if original has > 10 pages)
    if '__' in document_id:
        position=document_id.rfind('__')
        sub_part=document_id[position:]
    else:
        sub_part=''
    
    new_row.append(sub_part)
    cols.append('sub_part')

    # Detect language of text
    language=fasttext_language_predict(text ,model=ft_model) 
    language=language[0][0][0][-2:] 

    # Add language to new_row
    new_row.append(language)
    cols.append('language')

    # Counter for paragraphs
    base=int(0)

    # Get all paragraphs from all pages
    for page in document.pages:
        new_row, cols, x = print_paragraphs(page.paragraphs, text, new_row, cols, base)
        base+=x

    # Write new_row as a dataframe  
    new_df = pd.DataFrame([new_row], columns=cols)

    # Return dataframe
    return new_df

def print_paragraphs(paragraphs: Sequence[documentai.Document.Page.Paragraph], text: str, new_row: list, cols: list, base: int) -> None:
    if len(paragraphs)!=0:
        for x in range (len(paragraphs)):
            # Get the text of this paragraph
            paragraph_text=layout_to_text(paragraphs[x].layout, text)
            # Add text in new_row
            new_row.append(paragraph_text)
            # Create paragraph column for dataframe
            cols.append(f'p{base+x+1}')

        return new_row , cols, x+1
    else:
        return new_row , cols, 0

def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response

# Function to count the number of pages in .pdf
def get_nr_of_pages(file):
    readpdf = PyPDF2.PdfFileReader(file)
    totalpages = readpdf.numPages
    return totalpages


# This function checks if files are still to be processed
# These documents have already been processed into a .txt file
# It makes a list of these documents to not feed them to Google Document AI
def check_if_processed(file_to_check):
    
    documents=[]
 
    file=file_to_check
    if file_to_check.find('__') != -1:

        page=re.findall(r'__(.*)',file) 
        page=page[0][:-4]

        document_id=re.sub(page[0],'',file)
        document_id=re.sub(f'__{page}','',file)
        document_id=file[3:] 
        document_id=re.sub('__(.*)','',document_id)
        documents.append(document_id)

    # Check if file_to_check is in already processed documents list
    document_nr=file_to_check
    document_nr=file_to_check[3:]
    document_nr=re.sub('\.pdf','',document_nr)
    document_nr=re.sub('__(.*)','',document_nr) 
 
    if document_nr not in documents:
        return False
    else:
        return True
 
# This function processes the pdf
# It checks the number of pages to see if file needs to be split (DocumentAI accepts 10 pages max)
# After check it feeds the document to DocumentAI
# It returns a code for our app

def process_pdf(path,document_id,df):
 
    file=f'{document_id}.pdf'

    output_path=os.path.join('..','tmp','txt')
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    # Check if file is .pdf
    if file[-4:]=='.pdf': 

        document_id=file
        check=check_if_processed(file) 
        check=False
        if check==False:
 
            if os.path.exists(os.path.join(path,file)):
                file_path=os.path.join(path,file)
            elif os.path.exists(os.path.join(path,'too_large','split_10',file)):
                file_path=os.path.join(path,'too_large','split_10',file)
            else:
                file_path=os.path.join(path,file)

            # Max page size on Google Cloud = 10
            if get_nr_of_pages(file_path)<=10:
 
                # Run the process on the cloud
 
                new_df=process_document_ocr(project_id,location,processor_id,processor_version,file_path,document_id,mime_type,output_path)
 
                # Add new output to df
                df = pd.concat([df, new_df], ignore_index = True)

                print(f"Processing {document_id} : Done                                             ",end='\r') 
                return 'OK', f'Processed {document_id}'
            
            else:    
                # Copy pdf file with > 10 pages to error folder
                src_path = file_path
                dst_path = os.path.join(output_path,'too_large')
                
                if not os.path.exists(dst_path):
                    os.mkdir(dst_path)

                dst_file= os.path.join(dst_path,document_id)
                shutil.copy(src_path, dst_file)
                print(f'{document_id}: Too Large', end="\r")
                return 'LARGE','too_large file, has to be split'
 
        else:

            return 'NN','didn\'t need to check'
 