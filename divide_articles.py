import os
import pandas as pd
from alive_progress import alive_bar

doc_path = "./processed_data/NL/"
doc_list = os.listdir(doc_path)

divided = []
not_divided = []

divided_docs = {}

def divide (doc: str):
    doc = doc.split("Artikel")
    articles = {}
    articles["title"] = doc[0].replace("\n"," ")
    for i in range(1,len(doc)):
        articles[f"Article {i}"] = doc[i].replace("\n"," ")
    return articles
 
with alive_bar(len(doc_list)) as bar:       
    for doc in doc_list:
        with open (f"{doc_path}/{doc}","r") as f:
            text = f.read()
        if "Artikel" in text:
            articles = divide(text)
            divided.append(doc)
            divided_docs[doc] = articles
        else:
            not_divided.append(doc)
        bar()
        
df = pd.DataFrame.from_dict(divided_docs,orient="index")
df.to_csv("divided.csv")
with open ("not_divided.txt","w+",encoding="utf-8") as f:
    print(not_divided,file=f)