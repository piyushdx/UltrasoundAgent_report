from flask import Flask, render_template, request, Response
import openai
from flask import Flask, request, jsonify
import os
import openai
import json
import time
import multiprocessing
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from pdf_utils import PDFUtils
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

prompt = "Analyze the provided ultrasound report for abnormalities. Identify any parameter that deviates from the normal range and explain the implications."

prompt2 = """
[identity]
You are UltrasoundBot, the go-to expert on ultrasound reports with comprehensive knowledge.

[purpose]
Facilitate the doctor in comprehending the ultrasound report and formulating subsequent steps or recommendations. Whenever you get an ultrasound report Identify abnormal values step by step, ensuring thorough comprehension.
You talk to people like a human would talk to them.
If you are unsure of the answer you can get details related to specific reports and recommendations by calling the get_guidelines function. 

[limitation]
If the question is not relevant to ultrasound report, refrain from providing an answer."""

pdf_folder_path = "./text"
persist_directory = "./db"

# Create an instance of PDFUtils class
pdf_utils = PDFUtils(pdf_folder_path, persist_directory)

# Call the initialize_qa_chain method to initialize the QA chain
pdf_utils.initialize_qa_chain()

app = Flask(__name__)

def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4 # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def ask_function_calling(messages,function_descriptions):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions = function_descriptions,
        function_call="auto"
    )
    return response

def json_parser(string_data):
    start_index = string_data.find("{")
    end_index = string_data.rfind("}") + 1

    # Extract the JSON portion from the string
    json_string = string_data[start_index:end_index]

    # Parse the JSON string into a Python dictionary
    data = json.loads(json_string)
    return data

def get_reports(abnormalities,final_ans):

    if any(abnormalities):
        reports = "Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you.^_^"
        for key, value in abnormalities.items():
            print(key + ": " + value)
            reports += f"{key} : {value}\n\n"
            query = "waht are the CPT reports needs to be done for "+str(key)+ " "+str(value) + "\n"
            result = pdf_utils.chat_with_pdf_q(query)
            result += '^_^'
            reports += result
            print("============\n")
            print(result)
        final_ans += reports
    else:
        pass
    return final_ans

function_descriptions = [
    {
        "name": "get_guidelines",
        "description": "This function searches a PDF on clinical guidelines for ultrasound cpt reports. It should be called when asked about any reports,cpt reports, recommendations or next steps.",
        "parameters": {
            "type": "object",
            "properties": {
                "Question_string": {
                    "type": "string",
                    "description": "Provide a search query without stopwords to be used for searching within the clinical guidelines PDF."
                },
            },
            "required": ["Question_string"]
        }
    },
    {
        "name": "parse_report",
        "description": "this function called when user upload entire ultrasound report",
        "parameters": {
            "type": "object",
            "properties": {
                "Report_string": {
                    "type": "string",
                    "description": "Entire report which is uploaded by user."
                },
            },
            "required": ["Report_string"]
        }
    }
]

def get_guidelines(Question_string):
    result = pdf_utils.chat_with_pdf_q(Question_string)
    return str(result)

def parse_report(Report_string):
    history = [{"role": "system", "content": prompt}]
    history += [{"role": "assistant", "content": "Please Upload your ultrasound report."}]
    history += [{"role": "user", "content": str(Report_string)}]
    try:
        response = get_completion(history)
    except Exception as e:  
        print(e)
        response = "Oops! An issue with the OpenAI API. Please try again in a few minutes after clearing the chat.. \n "+str(e)
        return jsonify({"response": response})
    history += [{"role": "assistant", "content": str(response)}]
    response += "^_^"
    step2 = """
    create list of abnormalities
    [compulsory json output formate]
            {
                "abnormalities": { } //list of abnormalities Ex. "parameter" : "value","parameter" : "value",...
            }
    [thought_chain]
        populate "abnormalities" if any abnormalities in the report and return only json.

    """
    history += [{"role": "user", "content": str(step2)}]
    try:
        response3 = get_completion(history)
    except:
        response3 = "Oops! An issue with the OpenAI API. Please try again in a few minutes after clearing the chat." + str(e)
        history.append({"role": "assistant", "content": response3})
        return jsonify({"response": response3})   
    final_ans = response
    print(response3)
    data = json_parser(response3)
    abnormalities = data["abnormalities"]
    final_ans = get_reports(abnormalities,final_ans)    
    final_ans += "Please feel free to ask me any specific questions you have regarding the report. I'm here to help!😊"
    final_response = final_ans.split("^_^")
    return final_response

def function_call(ai_response):
    function_call = ai_response["choices"][0]["message"]["function_call"]
    function_name = function_call["name"]
    arguments = function_call["arguments"]
    print(function_name)
    if function_name == "get_guidelines":
        Question_string = eval(arguments).get("Question_string")
        return get_guidelines(Question_string)
    elif function_name == "parse_report":
        Report_string = eval(arguments).get("Question_string")
        return parse_report(Report_string)
    else:
        return

def remove_last_source_pages(text):
    count = text.count("Source Pages")
    
    if count > 1:
        last_index = text.rindex("Source Pages")
        text = text[:last_index]
    
    return text


class UltraBot():
    def __init__(self):
        self.chat_history = [
            {"role": "system", "content": prompt2}
        ]
        self.first_time = True
        self.function_descriptions = function_descriptions

    def clear_cache(self):
        self.chat_history = [
            {"role": "system", "content": prompt2}
        ]
        self.first_time = True
        self.function_descriptions = function_descriptions
        print("Chat History cleared.....")
        return jsonify({"status": "True"})

    def get_response(self, data):
        function_response = None
        query = data["query"]
        self.chat_history += [{"role": "user", "content": str(query)}]
        print(self.chat_history)
        messages = self.chat_history #+ [{"role": "user", "content": query}]
        try:
            response = ask_function_calling(messages,self.function_descriptions)
        except Exception as e:
            print("Function calling Error : ",e)
            response = "Apologies! You have exceeded the maximum token limit of 4097. Please clear the chat and try again.\n" + str(e)
            self.chat_history.append({"role": "assistant", "content": response})
            return jsonify({"response": response})   
        # while response["choices"][0]["finish_reason"] == "function_call":
        if response["choices"][0]["finish_reason"] == "function_call":
                if response["choices"][0]["message"]["function_call"]["name"] == "parse_report":
                    function_response = parse_report(query)
                    if isinstance(function_response,list):
                        final_response = function_response
                    else:
                        final_response = "Something wrong in response, please try again later.."

                else:
                    function_response = function_call(response)
                    messages.append({
                        "role": "function",
                        "name": response["choices"][0]["message"]["function_call"]["name"],
                        "content": function_response
                    })
                    try:
                        response = ask_function_calling(messages,self.function_descriptions)
                    except Exception as e:
                        print("Function calling Error : ",e)
                        response = "Apologies! You have exceeded the maximum token limit of 4097. Please clear the chat and try again.\n" + str(e)
                        self.chat_history.append({"role": "assistant", "content": response})
                        return jsonify({"response": response})
                    if isinstance(function_response.split('\n')[-1], str) and isinstance(response.choices[0].message["content"],str):
                        response.choices[0].message["content"] = response.choices[0].message["content"] +'\n'+ function_response.split('\n')[-1]
                        print(response.choices[0].message["content"])
                    else:
                        print(response)
                        print(function_response.split('\n')[-1])
                        response.choices[0].message["content"] = "Something wrong in response, please try again later.."
                    final_response = remove_last_source_pages(response.choices[0].message["content"])
        else:
            final_response = response.choices[0].message["content"]

        self.chat_history += [{"role": "assistant", "content": str(final_response)}]
        return jsonify({"response": final_response})
        
