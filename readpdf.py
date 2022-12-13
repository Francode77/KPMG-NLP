from pdfminer.high_level import extract_text

text = extract_text("Data/A/100/100-2019-014376.pdf")
text_list  = text.splitlines()
print(max(text_list,key=len))
print(len(max(text_list,key=len)))