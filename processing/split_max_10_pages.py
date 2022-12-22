# function to split .pdfs to fit Google cloud limit of max 10 pages

def split_max_page_10(path,document_id):
    import os
    from PyPDF2 import PdfFileWriter, PdfFileReader 

    path=os.path.join(path,'too_large')
    output_directory=os.path.join(path,'split_10')

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
 
    filename=f'{document_id}.pdf'

    inputpdf = PdfFileReader(open(f"{path}/{filename}", "rb"))
    x=int(0)
    i=int(0)

    if inputpdf.numPages>10:
        while i<inputpdf.numPages:
            output = PdfFileWriter()

            for i in range((10*x),(10*(x+1))):
                try: 
                    output.addPage(inputpdf.getPage(i))
                except:
                    break
            with open(f"{output_directory}/{document_id}__{x}.pdf", "wb") as outputStream:
                output.write(outputStream)
            print(f"{output_directory}/{document_id}__{x}.pdf ... DONE", end='\r')
            x+=1

        return 'OK'

    else:
        return 'FAIL'
 