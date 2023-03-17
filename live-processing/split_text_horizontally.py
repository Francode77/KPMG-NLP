import os
import numpy as np
import re
import pandas as pd

# FASTTEXT LANGUAGE detection 
import fasttext as ft 
ft_model = ft.load_model(os.path.join('..','preprocessing',"lid.176.ftz"))
def fasttext_language_predict(text, model = ft_model): 
  text = text.replace('\n', " ")
  prediction = model.predict([text]) 
  return prediction



def split_text_horizontally(input_path,document_id,language):
    
    # Function to split the processed .txt files that are NOT vertically split
    # based on paragraphs language detection 
    # in the dataframe obtained after google DocumentAI processing

    df=pd.DataFrame()

    input_csv=os.path.join('..','csv','NL_final_doc_paragraphs.csv')
    df=pd.read_csv(input_csv)

    # Set the paths 
    output_path_NL=os.path.join(input_path,language)
    output_path_FR=os.path.join(input_path,language)

    try:
        os.mkdir(output_path_NL)
        os.mkdir(output_path_FR)
    except:
        pass
 
    document_pdf=f'{document_id}.pdf'

    x=int (1)
    t_nl=int (1)
    t_fr=int (1)
    
    # This keeps a list to remember in what language we are right now
    p_language_list=[]

    # output paragraphs to text
    nl_text=str()
    fr_text=str()
    p_language='fr'
    if len(df[df['document_id']==document_pdf])!=0:

        while df[df['document_id']==document_pdf][f'p{x}'].values.astype(str)[0]!='nan':

            paragraph=df[df['document_id']==document_pdf][f'p{x}'].values.astype(str)[0]
            paragraph=re.sub('\\n',' ',paragraph)
            
            if len(paragraph)>44:
                p_language=fasttext_language_predict(paragraph)[0][0][0][-2:] 
                #print (f'{x} : {p_language} {paragraph[:63]}')    

            x+=1  

            if p_language!='nl' and p_language!='fr':
                try:
                    last_language=p_language_list[x-1]
                    p_language=last_language
                except:
                    last_language=''
            else: 
                p_language_list.append(p_language)
                    
            if 'Neerlegging-Dépôt' in paragraph:
                fr_text+=paragraph 
                fr_text+='\n'
                nl_text+=paragraph 
                nl_text+='\n'
                continue
                    
            if p_language=='nl':
                nl_text+=paragraph
                nl_text+='\n'
                t_nl+=1
                #nl_text.append('\n')

            if p_language=='fr':
                fr_text+=paragraph
                fr_text+='\n'
                t_fr+=1
                #fr_text.append('\n')

            # Break if we are at max paragraph column
            if x>(len(df.columns)-4): 
                break

        fr_txt=f'FR_{document_id}.txt'
        nl_txt=f'NL_{document_id}.txt'

        output_file_FR=os.path.join(output_path_FR,fr_txt)
        output_file_NL=os.path.join(output_path_NL,nl_txt)

        with open (output_file_NL,'w',encoding="utf-8") as fp:
            fp.write(nl_text)

        with open (output_file_FR,'w',encoding="utf-8") as fp:
            fp.write(fr_text)

        status=f'{document_pdf} has {x} paragraphs, NL : {t_nl}, FR: {t_fr}'

        return status
    else:

        return 'Could not process this file'