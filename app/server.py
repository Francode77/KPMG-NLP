from flask import Flask
from flask import request
from flask import Response
import requests
from flask import Flask, redirect, url_for, request,render_template,jsonify,make_response


import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)
 
# now we can import the module in the parent
# directory.

from process import process

TOKEN = 'TELEGRAM TOKEN'
app = Flask(__name__)
 
def parse_message(message):
    print("message-->",message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id,txt
 
def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
   
    r = requests.post(url,json=payload)
    return r
 
def tel_send_document(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
 
    payload = {
        'chat_id': chat_id,
        "document": "http://www.africau.edu/images/default/sample.pdf",
 
    }
 
    r = requests.post(url, json=payload)
 
    return r

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
       
        chat_id,txt = parse_message(msg)
        if txt == "hi":
            tel_send_message(chat_id,'Hi there!')

        elif txt == "file":
            tel_send_document(chat_id)

        elif txt =='clear':
            tel_send_message(chat_id,'hi\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n..')

        else:
            tel_send_message(chat_id,'Sorry, I didn\'t understand that..')
       
        return Response('ok', status=200)

    else:
        return "<h1>Welcome!</h1>"
        

@app.route('/input')
def input():
     return render_template('input.html')

@app.route('/feed_pdf',methods = ['GET','POST'])
def feed_pdf():
    if request.method == "POST":
        PDF=request.form['PDF']
        PDF+='.pdf'
        #print (PDF)
        output = process (PDF) 
        cla=output['cao']
        depot=output['depot']
        register=output['register'] 
        sum=output['sum']
        url=output['url']
        return render_template('output.html',cla=cla,depot=depot,register=register,sum=sum,url=url)
        
        
    if request.method == "GET":

        string="Please include the following:<br><b>area</b> int,<br>    <b>property-type</b> APARTMENT | HOUSE,<br>    <b>rooms-number</b> int,<br>    <b>zip-code</b> int,<br>    <b>land-area</b> Optional[int],<br>    <b>garden</b> Optional[bool],<br>    <b>garden-area</b> Optional[int],<br>    <b>equipped-kitchen</b> Optional[bool],<br>    <b>full-address</b> Optional[str],<br>    <b>swimming-pool</b> Optional[bool],<br>    <b>furnished</b> Optional[bool],<br>    <b>open-fire</b> Optional[bool],<br>    <b>terrace</b> Optional[bool],<br>    <b>terrace-area</b> Optional[int],<br>    <b>facades-number</b> Optional[int],<br>    <b>building-state</b> Optional[    NEW | GOOD | TO_RENOVATE | JUST_RENOVATED | TO_REBUILD"
        return (string)


if __name__ == '__main__':
   app.run(debug=True,port=80)