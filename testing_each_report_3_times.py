import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from config import config, environment, ip_config
import re
from ultrabot import UltraBot
# from utils import convert2text
import os
from text2json import *
app = Flask(__name__)
CORS(app, support_credentials=True)
import time
ultrabot = UltraBot()
from db_create import create_db
directory_path = './ChatBotUI/pdfs'


import json
def remove_null_keys(json_str):
  # Parse JSON string to dict
  try:
    data = json.loads(json_str)
  except Exception as e:
    print(f"Getting error in rempve null keys function... {e}")
  # Loop through keys and pop ones with null values
  for key in list(data.keys()):
    if data[key] == "Not Found":
      data.pop(key)

  # Convert updated dict back to JSON
  return json.dumps(data)


output_file_path = '/home/piyush/Work/UltrasoundAgent_report/output.txt'
# Check if the directory exists
if os.path.exists(directory_path):
    # Get the list of files in the directory
    files = os.listdir(directory_path)
    # Print the full path for each file
    for file in files:
        outputfile = open(output_file_path, 'a')
        try:
            for i in range(3):
                start_extra = time.time()
                full_path = os.path.join(directory_path, file)
                print(full_path)

                start = time.time()
                report_text = convert2text(SourceFile = str(full_path))
                print(report_text)
                end = time.time()
                print("The time of execution for convert2text is :",(end-start)," second")

                print("convert to text is done.")
                start = time.time()
                json_data = text_to_json(report_text)
                if "please try after sometime. issue @OpenAI side." in json_data:
                #    return jsonify({"message": json_data}), 400
                    print("problem at open is side")
                    continue
                end = time.time()
                print("The time of execution for text_to_json :",(end-start)," second")

                print(json_data)
                # print("---------------------------")
                start = time.time()
                json_data_pure = remove_null_keys(json_data)
                end = time.time()
                print("The time of execution for remove_null_keys :",(end-start)," second")
                print(json_data_pure)
                print("cleaned data................")
                data = {'query': str(json_data_pure), type: ''}
                end_extra =  time.time()
                output_data = ultrabot.get_response(data,extra_time=end_extra-start_extra)
                print("\n\nthis is output data......................... ::: \n")
                print(output_data)
                file_path = 'output.txt'
                if os.path.exists(file_path):
                    # If the file doesn't exist, create it
                    outputfile.write(str(i) +". "+ file)
                    outputfile.write("\n")
                    for line in output_data:
                        outputfile.write(line+"\n\n")
                    outputfile.write("\n")
                    print("done with writing")
                    # outputfile.writelines(output_data)
                # print(f"File '{file_path}' created and numbers 1 to 100 written.")
                else:
                    print(f"File '{file_path}' not exists. please create a file named {file_path}")
        finally:
            outputfile.close()
           
else:
    print(f"The directory '{directory_path}' does not exist.")
# if outputfile is not None:
#     outputfile.close()


# file_path = '/home/piyush/Work/UltrasoundAgent_report/output.txt'
# for i in range(3):
#     output_data = ["piyush","hello","this is me"]
#     file = "./adf/adf/fd"
#     if not os.path.exists(file_path):
#         # If the file doesn't exist, create it
#             outputfile = open(file_path, 'a')
#             outputfile.write(file + str(i))
#             outputfile.writelines(output_data)
#     # print(f"File '{file_path}' created and numbers 1 to 100 written.")
#     else:
#         print(f"File '{file_path}' already exists. Not creating the file.")
# outputfile.close()

# import os

# file_path = '/home/piyush/Work/UltrasoundAgent_report/output.txt'
# outputfile = None  # Initialize outputfile outside the loop
# outputfile = open(file_path, 'a')
# for i in range(3):
#     output_data = ["piyush", "hello", "this is me"]
#     file = "./adf/adf/fd"
#     if os.path.exists(file_path):
#         # If the file doesn't exist, create it
#         outputfile.write(file + str(i))
#         outputfile.write("\n")
#         for line in output_data:
#             outputfile.write(line+"\n\n")
#         outputfile.write("\n")
        
#         # outputfile.writelines(output_data)
#     # print(f"File '{file_path}' created and numbers 1 to 100 written.")
#     else:
#         print(f"File '{file_path}' not exists. please create a file named {file_path}")

# # Close the file outside the loop
# if outputfile is not None:
#     outputfile.close()