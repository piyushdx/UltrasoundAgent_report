import os
import requests # pip install requests

# API_KEY = "piyush@dxfactor.com_abaab3291ab8029766bc5eb6a3655270594ec2883bdfaf7184f01b25c1224a910c000f7c"
API_KEY = "jimifo3764@sesxe.com_a10c3cde2af4121daabd1c4fc64ddb23d28e166189dd5b001e52e0102953e778415ea1d1"

# Base URL for PDF.co Web API requests
BASE_URL = "https://api.pdf.co/v1"

# def convert2txt(args = None):

#     # The authentication key (API Key).
#     # Get your own by registering at https://app.pdf.co
#     API_KEY = "piyush@dxfactor.com_abaab3291ab8029766bc5eb6a3655270594ec2883bdfaf7184f01b25c1224a910c000f7c"


#     # Source PDF file
#     SourceFile = "/home/piyush/Work/UltrasoundAgent_report/US REPORTS/others/SKM_C65823071313500    2.pdf"
#     # Destination CSV file name
#     DestinationFile = "SKM_C65823071313500    2.txt"


#     uploadedFileUrl = uploadFile(SourceFile)
#     if (uploadedFileUrl != None):
#         return convertPdfToText(uploadedFileUrl, DestinationFile)
def convert2text(args = None):

    # The authentication key (API Key).
    # Get your own by registering at https://app.pdf.co
    API_KEY = "jimifo3764@sesxe.com_a10c3cde2af4121daabd1c4fc64ddb23d28e166189dd5b001e52e0102953e778415ea1d1"


    # Source PDF file
    SourceFile = "ChatBotUI/static/pdf/uploaded.pdf"
    # Destination CSV file name
    DestinationFile = "SKM_C65823071313500    2.txt"


    uploadedFileUrl = uploadFile(SourceFile)
    if (uploadedFileUrl != None):
        return convertPdfToText(uploadedFileUrl, DestinationFile)

def convertPdfToText(uploadedFileUrl, destinationFile):
    """Converts PDF To Text using PDF.co Web API"""
    
    API_KEY = "jimifo3764@sesxe.com_a10c3cde2af4121daabd1c4fc64ddb23d28e166189dd5b001e52e0102953e778415ea1d1"

    # PDF document password. Leave empty for unprotected documents.
    Password = ""
    # Comma-separated list of page indices (or ranges) to process. Leave empty for all pages. Example: '0,2-5,7-'.
    Pages = ""
    # Base URL for PDF.co Web API requests
    BASE_URL = "https://api.pdf.co/v1"

    # Prepare requests params as JSON
    # See documentation: https://apidocs.pdf.co
    parameters = {}
    parameters["name"] = os.path.basename(destinationFile)
    parameters["password"] = Password
    parameters["pages"] = Pages
    parameters["url"] = uploadedFileUrl

    # Prepare URL for 'PDF To Text' API request
    url = "{}/pdf/convert/to/text".format(BASE_URL)

    # Execute request and get response as JSON
    response = requests.post(url, data=parameters, headers={ "x-api-key": API_KEY })
    if (response.status_code == 200):
        json = response.json()

        if json["error"] == False:
            #  Get URL of result file
            resultFileUrl = json["url"]            
            # Download result file
            r = requests.get(resultFileUrl, stream=True)
            if (r.status_code == 200):
                report_text = b""
                with open(destinationFile, 'wb') as file:
                    for chunk in r:
                        file.write(chunk)
                        report_text += chunk
                print(report_text)
                print("done with pdf to txt")
                # print(f"Result file saved as \"{destinationFile}\" file.")
                return report_text
            else:
                return f"Request error: {response.status_code} {response.reason}"
        else:
            # Show service reported error
            return str(json["message"])
    else:
        return f"Request error: {response.status_code} {response.reason}"


def uploadFile(fileName):
    """Uploads file to the cloud"""
    # Base URL for PDF.co Web API requests
    BASE_URL = "https://api.pdf.co/v1"
    API_KEY = "jimifo3764@sesxe.com_a10c3cde2af4121daabd1c4fc64ddb23d28e166189dd5b001e52e0102953e778415ea1d1"
    
    # 1. RETRIEVE PRESIGNED URL TO UPLOAD FILE.

    # Prepare URL for 'Get Presigned URL' API request
    url = "{}/file/upload/get-presigned-url?contenttype=application/octet-stream&name={}".format(
        BASE_URL, os.path.basename(fileName))
    
    # Execute request and get response as JSON
    response = requests.get(url, headers={ "x-api-key": API_KEY })
    if (response.status_code == 200):
        json = response.json()
        
        if json["error"] == False:
            # URL to use for file upload
            uploadUrl = json["presignedUrl"]
            # URL for future reference
            uploadedFileUrl = json["url"]

            # 2. UPLOAD FILE TO CLOUD.
            with open(fileName, 'rb') as file:
                requests.put(uploadUrl, data=file, headers={ "x-api-key": API_KEY, "content-type": "application/octet-stream" })

            return uploadedFileUrl
        else:
            # Show service reported error
            print(json["message"])    
    else:
        print(f"Request error: {response.status_code} {response.reason}")

    return None


# if __name__ == '__main__':
#     main()

            