
def combine_txt_files(path,output_path):
    import os
    import re
    from os import listdir

    entries = listdir(path)

    for file in entries:
        
        if file.find('__') != -1: 

            page=re.findall(r'__(.*)',file) 
            page=page[0][:-4]

            document_id=re.sub(page[0],'',file)
            document_id=re.sub(f'__{page}','',file)
 
            file=os.path.join(path,file)

            x=int(0)
            data=str()

            with open(file,encoding="utf-8") as fp:
            
                data += fp.read()

            # now we have the output file ready 
            output=os.path.join(output_path,document_id)

            with open (output, 'a',encoding="utf-8") as fp:
                fp.write(data)


# You can now safely delete the .txt part files in input_path