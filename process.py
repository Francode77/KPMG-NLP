# First start

#Open windows shell
#type : ngrok http 5000
#Copy https://96ba-78-23-2-11.eu.ngrok.io -> http://localhost:80

TOKEN = "5852402848:AAEo_0pts2uWXfEoBSC_W4kgml3mBxAslQc"

# Get the 
# Setup the webhook
# https://api.telegram.org/bot5852402848:AAEo_0pts2uWXfEoBSC_W4kgml3mBxAslQc/setWebhook?url=https://96ba-78-23-2-11.eu.ngrok.io


"""
pip install --upgrade google-cloud-documentai
pip install fasttext
pip install pyPDF2
"""

import os 
import shutil
import requests
import pandas as pd
import json
import shutil
from os import listdir

from processing.split_text_horizontally import split_text_horizontally
from processing.get_abstr_summary import get_abstr_summary
from processing.process_cloud import process_document, process_document_ocr,process_pdf,get_nr_of_pages,check_if_processed
from processing.split_max_10_pages import split_max_page_10
from processing.combine_txt_files import combine_txt_files
from processing.split_pdf_vertically import split_file,splitpage

TOKEN = "5852402848:AAEo_0pts2uWXfEoBSC_W4kgml3mBxAslQc"


def get_comitee (file_id:str):
    with open("../csv/comite_list.txt") as f:
        pcs_from_text = f.read()

    pcs_from_text = pcs_from_text.replace("\n","")
    res = json.loads(pcs_from_text)

    try:
        number = file_id.split("-")[0]
        return number, res[str(number)]
    except KeyError:
        return "Invalid number of comitee"
 

def make_link(document_id):
    link_base = 'https://public-search.werk.belgie.be/website-download-service/joint-work-convention/'
    pos=document_id.find('-') 
    JC_num=str(document_id)[:pos]+ '/'

    full_link = link_base + str(JC_num)+ str(document_id)
    return full_link

def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
   
    r = requests.post(url,json=payload)
    return r

def get_details(document_id):
    file=f'{document_id}.txt'
    file_path=os.path.join('..','tmp',file)
    with open (file_path,encoding='UTF-8') as f:
        text=f.read()
    cao_nr='Not Found'
    depot='Not Found'
    registr='Not Found'
    pos_cao_nr=text.find('N°: ')
    if pos_cao_nr!=-1:
        cao_nr=text[pos_cao_nr+3:pos_cao_nr+16]
    pos_depot=text.find('Neerlegging-Dépôt: ')
    if pos_depot!=-1:
        depot=text[pos_depot+19:pos_depot+29]
    pos_regr=text.find('Regist.-Enregistr.: ')
    if pos_regr!=-1:
        registr=text[pos_regr+20:pos_regr+30]
    
    return cao_nr, depot, registr

def process (document_id):
    
    chat_id='409700231'
    
    language='NL' 
    path=os.path.join('..','tmp')
    
    df=pd.DataFrame()
    processed_by_cloud_status='FALSE'
    split_10_status='FALSE'
    toolarge='FALSE'
    returnlist={'cao':'None','depot':'None','register': 'None','sum': 'None','url': 'None'}

    PC_nr, PC=get_comitee(document_id)

    if '.pdf' in document_id:
        document_id=document_id[:-4]
        if os.path.exists(os.path.join('tmp',f'{document_id}.pdf')):
            tel_send_message(chat_id,f'New CAO alert from Joint Commite: {PC_nr} ({PC})')
    tel_send_message(chat_id,f'New CAO alert!\n\n Joint Commite: {PC_nr} ({PC})')

    # TEST if WE can SPLIT a FILE
    v_split_status_code=split_file(path,document_id,language)
    
    if v_split_status_code=="Success": 
        tel_send_message(chat_id,f'Status: Vertical Split.. : Done.')        
        # MOVE pdf FILE TO /tmp
        path_PDF=os.path.join(path,'pdf')
        src_path = os.path.join(path_PDF,f'{document_id}.pdf')
        dst_path = os.path.join(path)
        dst_file= os.path.join(dst_path,f'SPLIT_{document_id}.pdf')
        shutil.copy(src_path, dst_file) 
        #tel_send_message(chat_id,f'Moved the SPLIT pdf')
        processed_by_cloud_status,stattus=process_pdf(path,f'SPLIT_{document_id}',df)       
        # MOVE txt FILE TO /tmp        
        path_txt=os.path.join(path,'txt')
        src_path = os.path.join(path_txt,f'SPLIT_{document_id}.txt')
        dst_path = os.path.join(path)
        dst_file= os.path.join(dst_path,f'{document_id}.txt')
        shutil.copy(src_path, dst_file) 

    if v_split_status_code!="Success": 
        tel_send_message(chat_id,f'Status: Horizontal Split.. : Done.')
        result=split_text_horizontally(path,document_id,language)
        tel_send_message(chat_id,f'Status: {result}')

        if result=='Could not process this file': 
            return returnlist
        # MOVE FILE TO /tmp
        
        path_NL=os.path.join(path,'NL')
        src_path = os.path.join(path_NL,f'NL_{document_id}.txt')
        dst_path = os.path.join(path)
        dst_file= os.path.join(dst_path,f'{document_id}.txt')
        shutil.copy(src_path, dst_file) 
        #tel_send_message(chat_id,f'Moved {document_id}.txt')
 
    tel_send_message(chat_id,f'Feeding to Google DocumentAI.. ')

    if processed_by_cloud_status=='LARGE':
        split_10_status=split_max_page_10(path,document_id)

        if split_10_status=='OK':
            toolarge=1
            path_large=os.path.join(path,'too_large','split_10')
            tel_send_message(chat_id,f'Hold on, Google DocumentAI requires a split.. ')

            for filename in listdir(path_large):
                file=filename[:-4]
                processed_by_cloud_status,stattus=process_pdf(path,file,df)
            
        if toolarge==1:
            input_path=os.path.join(path,'txt')
            output_path=path
            combine_txt_files(input_path,output_path)
    
    tel_send_message(chat_id,f'Preprocessing: Done.')

    cao_nr, depot, registr = get_details(document_id) 
    
    tel_send_message(chat_id,f'Here are the details:\n____________ \nCAO N°: {cao_nr}\nDeposited: {depot}\nRegistered: {registr}\n')

    summary='Not detected'
    
    tel_send_message(chat_id,f'Working on a summary (this can take a while).. ')
    # Summarizet the text
    summary=get_abstr_summary(document_id,language)

    tel_send_message(chat_id,f'Summary:\n\n{summary}')
    url='https://public-search.werk.belgie.be/website-download-service/joint-work-convention/'
    url=make_link(document_id)    
    url+=f'.pdf'
    tel_send_message(chat_id,f'Link: {url} ')



    returnlist={'PC':PC,'cao':cao_nr,'depot':depot,'register':registr,'sum':summary,'url':url}
    return returnlist

    

"""

    # Now we have a text file
    text_file=f'{language}_{document_id}.txt'
 
    text_file_path=os.path.join('..','processed_data','NL',text_file)
    try:
        with open (text_file_path,encoding="UTF-8") as f:
            text=f.read()
    except:
        text_file=f'{document_id}.txt'
        text_file_path=os.path.join('..','processed_data','NL',text_file)

        with open (text_file_path,encoding="UTF-8") as f:
            text=f.read()
    
    # RETURN TEXT?
"""

            