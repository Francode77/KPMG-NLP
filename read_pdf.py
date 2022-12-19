from os import listdir
import fitz
import alive_progress






def classifier(pdf_file):
    with open(pdf_file,"rb") as f:
        pdf = fitz.open(f)
        res = []
        for page in pdf:
            image_area = 0.0
            text_area = 0.0
            for b in page.get_text("blocks"):
                if '<image:' in b[4]:
                    r = fitz.Rect(b[:4])
                    image_area = image_area + abs(r)
                else:
                    r = fitz.Rect(b[:4])
                    text_area = text_area + abs(r)
            if image_area == 0.0 and text_area != 0.0:
                res.append(1)
            if text_area == 0.0 and image_area != 0.0:
                res.append(0) 
        return res
    
    
a = listdir("data/A")
b = listdir("data/B")

text = []
image = []

with alive_progress.alive_bar() as bar :
    for directory in a:
        for document in listdir(f"data/A/{directory}"):
            result = classifier(f"data/A/{directory}/{document}")
            if result == 0:
                text.append(document)
            else:
                image.append(document)
            bar()

with alive_progress.alive_bar() as bar :
    for directory in b:
        for document in listdir(f"data/B/{directory}"):
            result = classifier(f"data/B/{directory}/{document}")
            if result == 0:
                text.append(document)
            else:
                image.append(document)
            bar()
with open("text.txt","w+",encoding="utf-8") as f:
    print(text,file=f)
with open("image.txt","w+",encoding="utf-8") as f:
    print(image,file=f)