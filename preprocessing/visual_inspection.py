# Program to quickly visualize the processed .txt documents

import os
from os import listdir
import time 

# FASTTEXT LANGUAGE detection 
import fasttext as ft 
ft_model = ft.load_model("lid.176.ftz") 
def fasttext_language_predict(text, model = ft_model): 
  text = text.replace('\n', " ")
  prediction = model.predict([text]) 
  return prediction

# Visual inspection of files
input_path=os.path.join('../processed_data','NL')

target_language='NL'
opposite_language='FR'

input_path=os.path.join('../processed_data',target_language)
opposite_path=os.path.join('../processed_data',opposite_language)

files_in_path=listdir(input_path)
for file in files_in_path:
    filename=os.path.join(input_path,file)
    with open(filename,encoding="utf-8") as f:
        text = f.read()
        lines_up = text.count('\n')+2
        detected_language=fasttext_language_predict(text, model = ft_model)[0][0][0][-2:]  

        if detected_language.upper()==target_language:
            document_id=file[3:]

            with open (f'{opposite_path}/{opposite_language}_{document_id}',encoding="utf-8") as f:
                opposite_text=f.read()
            opp_detected_language=fasttext_language_predict(opposite_text, model = ft_model)[0][0][0][-2:]  
 
            print (text[500:],'\n') 
            print(f"{file} {detected_language} - {opp_detected_language}",end='\n')
            time.sleep(0.77)
            print('\033[2J')
