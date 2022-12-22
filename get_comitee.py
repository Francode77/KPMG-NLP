import os
import json

with open("comite_list.txt") as f:
    text = f.read()

text = text.replace("\n","")
res = json.loads(text)

def get_comitee (number: int):
    try:
        return res[str(number)]
    except KeyError:
        return "Invalid number of comitee"

print(get_comitee(120))