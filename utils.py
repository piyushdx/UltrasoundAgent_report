# from flask import Flask, render_template, request
# import requests
# import os
# from pdf2text import *
# import requests

# API_KEY = "pankti.fadia.dxfactor@gmail.com_46d8850f32dcc4f07eb2ced82bc9af5e67f94b2b1f1b0804fd097dc7c150f184a895f862"

# # Base URL for PDF.co Web API requests
# BASE_URL = "https://api.pdf.co/v1"

# # def convert2text(pdf_file):    
# #     print(pdf_file.filename)
# #     print("works")
# #     url = f"{BASE_URL}/file/upload/get-presigned-url?name={pdf_file.filename}"
# #     response = requests.get(url, headers={"x-api-key": API_KEY})
# #     upload_url = response.json()["presignedUrl"]
# #     uploaded_url = response.json()["url"]

# #     requests.put(upload_url, data=pdf_file, 
# #                     headers={"x-api-key":API_KEY, "content-type":"application/octet-stream"})

# #     # Convert PDF to Text
# #     url = f"{BASE_URL}/pdf/convert/to/text"
# #     response = requests.post(url, json={
# #         "name": "output.txt",
# #         "url": uploaded_url
# #     }, headers={"x-api-key": API_KEY})
# #     print("*******************")
# #     print(response.json())
# #     text = response.json()["text"]
# #     print(text)
# #     # return text


# def convert2text(args = None):

#     # The authentication key (API Key).
#     # Get your own by registering at https://app.pdf.co
#     API_KEY = "pankti.fadia.dxfactor@gmail.com_46d8850f32dcc4f07eb2ced82bc9af5e67f94b2b1f1b0804fd097dc7c150f184a895f862"


#     # Source PDF file
#     SourceFile = "uploaded.pdf"
#     # Destination CSV file name
#     DestinationFile = "40707_2.txt"


#     uploadedFileUrl = uploadFile(SourceFile)
#     if (uploadedFileUrl != None):
#         return convertPdfToText(uploadedFileUrl, DestinationFile)