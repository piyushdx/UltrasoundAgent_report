# from flask import Flask, render_template, request, Response
import openai
from flask import jsonify
import os
import openai
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from pdf_utils import PDFUtils
# from dotenv import load_dotenv
# load_dotenv()
from insights import insightsAll
from datetime import datetime

openai.api_key = os.environ.get("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
# prompt = "Identify"
# prompt = "Analyze the provided ultrasound report for abnormalities. Identify any parameter that deviates from the normal range and explain the implications."
# prompt = "Analyze the provided ultrasound report for abnormalities. Identify any parameter that deviates from the normal range and explain the implications."

# prompt = "Your task is to check each parameter of provided ultrasound report json and determine whether there are any parameters that deviate from the standard or normal range of values, as such deviations may suggest potential issues.keep US imaging guidelines in mind. think step by step..."
prompt = """
Your Task is to create JSON file of abnormalities.

<INSIGHTS_DATA>
"""
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

# app = Flask(__name__)


def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def ask_function_calling(messages, function_descriptions):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto"
    )
    return response


def json_parser(string_data):
    '''
    Use:
        used to extract only json from the text.

    Parameter:
        string_data : String

    Output:
        json_string : String
    '''
    start_index = string_data.find("{")
    end_index = string_data.rfind("}") + 1

    # Extract the JSON portion from the string
    json_string = string_data[start_index:end_index]

    # Parse the JSON string into a Python dictionary
    # data = json.loads(json_string)
    return json_string


def flatten_json(json_data, parent_key='', flattened_data={}):
    for key, value in json_data.items():
        new_key = parent_key + '.' + key if parent_key else key
        if isinstance(value, dict):
            flatten_json(value, new_key, flattened_data)
        else:
            flattened_data[new_key] = value
    new_flatten = {
        "abnormalities": {

        }
    }

    for key, value in flattened_data.items():
        new_flatten["abnormalities"][key.split(".")[-1]] = value
    return new_flatten


def remove_AC(abno):
    for key, value in abno["abnormalities"].items():
        if key == "AC value in pctl":
            print("key found")
            del abno[key]
    print(abno)
    return abno


def get_reports(abnormalities,negative_finding_keys):
    for key in negative_finding_keys:
        abnormalities[key] = ""
    print(abnormalities)
    print("above are all the possible abnormalities........................................................")
    if any(abnormalities):
        reports = "Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you.^_^"
        for key, value in abnormalities.items():
            if str.lower(value) == "not seen":
                continue
            print(str(key) + ": " + str(value))
            reports += f"{str(key)} : {str(value)}\n\n"
            query = "I would like comprehensive guidelines for the " + str(key) + " "+str(value) + " along with CPT reports.\n"
            result = pdf_utils.chat_with_pdf_q(query)
            result += '^_^'
            reports += result
        final_ans = reports
    else:
        final_ans = "No Abnormalities Found."  # create fail mechanism
    return final_ans


function_descriptions = [
    {
        "name": "get_guidelines",
        "description": "This function searches a PDF on clinical guidelines for ultrasound cpt reports. It should be called when asked about any reports, cpt reports, recommendations or next steps.",
        "parameters": {
            "type": "object",
            "properties": {
                "Question_string": {
                    "type": "string",
                    "description": "user input for searching within a PDF containing clinical guidelines"
                },
            },
            "required": ["Question_string"]
        }
    },
    {
        "name": "parse_report",
        "description": "Use this when user upload ultrasound report json",
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

# def get_relevant_docs_from_pdf(query):
#     """
#     imput : query
#     purpose : to ger relavant chunks from the pdf
#     output : relevant_chunks_from_pdf
#     """
#     db = Chroma(persist_directory="./db", embedding_function=OpenAIEmbeddings())
#     relevant_chunks_from_pdf = db.similarity_search(query)
#     return relevant_chunks_from_pdf
# def get_answer_from_pdf(query):
#     # print(docs[0].page_content)
#     relevant_chunks_from_pdf = get_relevant_docs_from_pdf(query)
#     prompt_template = """
#     [Output sample]
#         Key Analysis: // just explain what is the problem.
#         Recommendation: // contain cpt reports.

#     [Example] 
#         Question: I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
#         Output : 
#             Key Analysis: AC &lt; 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
#                 actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
#                 Circumference ≤10th percentile.
            
#             Recommendation:
#                  Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
#                  Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
#                 can be performed once or twice weekly
#                  Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
#                 weekly
#                  Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
#                 performed every 2 to 4 weeks if complete anatomy ultrasound previously performed


#     [RULES]
#         1. Strictly Adhere closely to the provided <output sample>.use <example> for your refrence.
#         2. Ensure that your response should be concise with Structured bullet point.
#         3. remove suspected results if know results are given. 
#         4. if no known results found then suspected results.

#     [init]
#         Strictly follow the <RULES>.
#         think step by step..."""
    
#     query_with_context = f"""
#     [Context]
#     {str(relevant_chunks_from_pdf)}
    
#     [Question]
#     {query}"""
    
#     final_answer = get_completion([{"role": "system", "content": prompt_template}, {"role": "user", "content": query_with_context}])
#     print("below is the final answer............")
#     print(final_answer)

def get_guidelines(Question_string):
    # que_prompt = """ related to obstetrical Replace abbreviations with full forms, except cpt/CPT """
    # Question_string = get_completion([{"role": "system", "content": que_prompt},{"role": "user", "content": Question_string}])
    print(Question_string)
    try:
        Question_string = get_completion([{"role": "system", "content": """Your task is to replace all obstetrical abbreviations in the given text with their full forms in (), except for "CPT(Current Procedural Terminology)". Please make sure to provide the expanded versions of the abbreviations wherever possible."""}, {
                                         "role": "user", "content": str(Question_string)}])
    except Exception as e:
        print("Error: "+str(e))
        return "Not found please try again."
    print("Question : ", Question_string)
    result = pdf_utils.chat_with_pdf_q(Question_string)
    # result = get_answer_from_pdf(Question_string)
    return str(result)

# def get_abno_biometry(Report_string):
    # history = [{"role": "system", "content": "You have comprehensive knowledge regarding ultrasound reports. If any of the measurements provided (AC, BPD, FL, HC) in the report and if they are below the 10th percentile, consider them as abnormal.check for each parameter and think step by step..."}]
    history = [{"role": "system", "content": "You possess extensive expertise in analyzing ultrasound reports. According to US imaging guidelines, any value for AC, BPD, FL, or HC that falls below the 10th percentile is considered an abnormality."}]
    history += [{"role": "user",
                 "content": "I require assistance with my ultrasound report."}]
    history += [{"role": "assistant",
                 "content": "Please Upload your ultrasound report in json formate."}]
    history += [{"role": "user", "content": str(Report_string)}]
    response = get_completion(history)
    # print(response)
    history += [{"role": "assistant", "content": str(response)}]
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
    response3 = get_completion(history)
    print(response3)
    print("first response3....")
    temp_history = [
        {"role": "system", "content": """check if json contains "AC value in ptcl" < 10th percentile. if it contains then replace it with "fetal growth restriction Abdominal Circumference(AC) < 10th percentile" in json of abnormalities """}]
    temp_history += [{"role": "user", "content": str(response3)}]
    response3 = get_completion(temp_history)
    print(response3)
    print(" response 3 -----------------")
    return response3


def merge_abno(data1, data2):
    '''
    data1 : str
    data2 : str

    merge data1 and data2

    return : json
    '''
    print(type(data1), type(data2))
    # data1 = json.loads(data1)
    # data2 = json.loads(data2)
    data1["abnormalities"].update(data2["abnormalities"])
    return data1


def get_ratios(insights, reportString):
    ratios_list = ["FL/AC in %", "FL/BPD in %", "FL/HC in %", "HC/AC in %"]
    ratios_range_list = ["FL/AC normal range", "FL/BPD normal range",
                         "FL/HC normal range", "HC/AC normal range"]
    for index in range(len(ratios_list)):
        if ratios_list[index] in reportString.keys():
            if ratios_range_list[index] in reportString.keys():
                insights += "["+str(ratios_list[index])+"]"+":\n"
                insights += ratios_range_list[index]+":" + \
                    reportString[ratios_range_list[index]] + "\n\n"
    return insights


def get_insights(reportString, insightsAll):
    insights = "Strictly Remember the following Knowledge when determining whether a specific parameter is Normal OR Abnormal.\n"
    # flag = 0
    for key, value in reportString.items():
        if key in insightsAll.keys():
            insights += "["+str(key)+"]"+":\n"
            insights += insightsAll[key]["normal_values"] + \
                "\n" + insightsAll[key]["abnormal_values"] + "\n\n"
            # flag += 1
            # if flag == 3:
            #     break
    insights = get_ratios(insights, reportString)
    print(insights)
    return insights


def get_abnormal_keys(json_data):

    abnormal_keys = []

    for key, value in json_data["abnormalities"].items():
        if value == "Abnormal":
            abnormal_keys.append(key)
        if "AFI cm value" in abnormal_keys and "AFI pctl value" in abnormal_keys:
            abnormal_keys.remove("AFI pctl value")
    return abnormal_keys

def get_abnormal_keys_comment(json_data):

    abnormal_keys = []

    for key, value in json_data["obstetric_complications"].items():
        abnormal_keys.append(value)
    return abnormal_keys


def get_final_abnormalities(abnormal_keys, json_data,mvp_flag,ageFlag):
    abnormalities = {}
    for key in abnormal_keys:
        if key in json_data.keys():
            if key == "AFI cm value":
                abnormalities["Amniotic Fluid Abnormalities AFI ≥24cm"] = json_data[key]
            else:    
                abnormalities[key] = json_data[key]
    if mvp_flag:
        abnormalities["confirmed diagnosis of polyhydramnios"] = "maximum vertical pocket(MVP) ≥8cm."
    if ageFlag:
        abnormalities["Socio-Demographic Risk Factors (maternal age)"] = "Age ≥ 35"
    new_json = {
        "abnormalities": abnormalities
    }

    return new_json

def get_age_edd(EstabDD,ExamDate,Age,ageFlag):
    ageFlag = False
    try:
        estab_date = datetime.strptime(EstabDD, "%m-%d-%Y")
        exam_date = datetime.strptime(ExamDate, "%m-%d-%Y")
        final_age = (estab_date - exam_date).days/365 + int(Age.split('yr')[0]) + int(Age.split('yr')[1].split('m')[0])/12

        if final_age > 35:
            ageFlag = True
    except Exception as E:
        print(str(estab_date)+str(exam_date)+str(final_age)+"\n"+"may be any of the above missing....")
        try:
            if Age>34:
                ageFlag = True
        except Exception as e:
            pass
    return ageFlag

def get_not_seen_mvp_edc(reportString):
    final_ans = "The following were not seen in the utlrasound:\n\n"
    # if 'Not seen' in reportString.values():

    EstabDD = None
    EDD = None
    ExamDate = None
    Age = None
    ageFlag = False

    q_list = []
    for k, v in reportString.items():
        if str.lower(v) == "not seen":
            final_ans += str(k)+"\n"
        if str(k) == "Q1 avg value in cm" or str(k) == "Q2 avg value in cm" or str(k) == "Q3 avg value in cm" or str(k) == "Q4 avg value in cm":
            value = float(v.split(' ')[0])
            if value > 4.0:
                q_list.append(float(v.split(' ')[0]))
        if str(k) == "EstabDD":
            EstabDD = str(v) 
        if str(k) == "EDD":
            EDD = str(v)
        if str(k) == "Exam Date":
            ExamDate = str(v)
        if str(k) == "Age":
            Age = str(v)

    if EstabDD is not None:
        ageFlag = get_age_edd(EstabDD,ExamDate,Age,ageFlag)
    elif EDD is not None:
        ageFlag = get_age_edd(EDD,ExamDate,Age,ageFlag)
    else:
        pass

    final_ans += "\nPlease conduct ultrasound again as soon as possible.^_^"

    sum_mvp = sum(q_list)
    flag = False
    if sum_mvp > 8.0:
        flag = True
    if len(final_ans) < 110:
        final_ans = ""
    return final_ans,flag,ageFlag

prompt_comment = """You are expert in understanding ultrasound Reports."""

def get_negative_findings(reportString):
    try:
        history = [{"role": "system", "content": prompt_comment}]
        history += [{"role": "user", "content": "give me names of obstetric complications from below text\n"+str(reportString["Comment"])}] # 
        try:
            # it will get me a json which contains possible abnormalities
            response3 = get_completion(history)
        except Exception as e:
            print("Function calling Error : ", e)
            response3 = "Oops! An issue with the OpenAI API. Can you please try again in a few minutes after clearing the chat."
            history.append({"role": "assistant", "content": response3})
            return jsonify({"response": response3})
        print(response3)
        print("above must be a list..")
        history += [{"role": "assistant", "content": str(response3)}]
        step2 = """
        create JSON of obstetric complications
        [compulsory JSON output formate]
                obstetric_complications = {1:"",2:""} // //list of abnormalities Ex. 1 : "<obstetric_complications> name",2 : "<obstetric_complications> name",...
        [thought_chain]
            populate <obstetric_complications> if report has any obstetric complications and return only JSON.    
        """
        history += [{"role": "user", "content": str(step2)}]
        print(history)
        try:
            # it will get me a json which contains possible abnormalities
            response3 = get_completion(history)
        except Exception as e:
            print("Function calling Error : ", e)
            response3 = "Oops! An issue with the OpenAI API. Can you please try again in a few minutes after clearing the chat."
            history.append({"role": "assistant", "content": response3})
            return jsonify({"response": response3})
        print(response3)
        abnormal_keys = get_abnormal_keys_comment(json.loads(json_parser(response3)))
        print(abnormal_keys)
        return abnormal_keys
    except Exception as E:
        print("No negative connotation is fond in the Comment")
        return []

def parse_report(Report_string):
    print("------------------- \nParsing Report \n------------------")
    history = [{"role": "system", "content": prompt.replace("<INSIGHTS_DATA>", get_insights(
        json.loads(Report_string), insightsAll))+"\n"+Report_string}]
    step2 = """
    create list of abnormalities
    [compulsory json output formate]
            {
                "abnormalities": { } //list of abnormalities Ex. "<parameter>" : "<Normal OR Abnormal>","<parameter>" : "<Normal OR Abnormal>",...
            }
    [thought_chain]
        populate "<parameter>" : "<Normal OR Abnormal>" if any abnormalities in the report and return only json.    
    """
    history += [{"role": "user", "content": str(step2)}]
    try:
        # it will get me a json which contains possible abnormalities
        response3 = get_completion(history)
    except Exception as e:
        print("Function calling Error : ", e)
        response3 = "Oops! An issue with the OpenAI API. Can you please try again in a few minutes after clearing the chat."
        history.append({"role": "assistant", "content": response3})
        return jsonify({"response": response3})
    negative_finding_keys = get_negative_findings(json.loads(json_parser(Report_string)))
    abnormalities = response3
    print(abnormalities)
    print("above are intermediate things............")
    abnormal_keys = get_abnormal_keys(json.loads(json_parser(abnormalities)))
    final_ans, mvp_flag,ageFlag = get_not_seen_mvp_edc(json.loads(json_parser(Report_string)))
    abnormalities = str(get_final_abnormalities(abnormal_keys, json.loads(json_parser(Report_string)),mvp_flag,ageFlag)["abnormalities"]).replace("'", "\"")
    print(abnormalities)
    print("Above are final Abnormalities....................")
    final_ans += get_reports(json.loads(abnormalities),negative_finding_keys)
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
            {"role": "system", "content": prompt2},
            {"role": "user", "content": "hey"},
            {"role": "assistant", "content": "Hi! How can i hlep you today ?"}
        ]
        self.first_time = True
        self.function_descriptions = function_descriptions

    def clear_cache(self):
        # user = data['email']
        self.chat_history = [
            {"role": "system", "content": prompt2},
            {"role": "user", "content": "hey"},
            {"role": "assistant", "content": "Hi! How can i hlep you today ?"}
        ]
        self.first_time = True
        self.function_descriptions = function_descriptions
        print("Chat History cleared.....")
        return jsonify({"status": "True"})

    def get_response(self, data):
        function_response = None
        query = data["query"]
        self.chat_history += [{"role": "user", "content": str(query)}]
        messages = self.chat_history  # + [{"role": "user", "content": query}]
        try:
            response = ask_function_calling(
                messages, self.function_descriptions)
        except Exception as e:
            print("Function calling Error : ", e)
            response = "Apologies! You have exceeded the maximum token limit of 4097. Please clear the chat and try again.\n"
            self.chat_history.append(
                {"role": "assistant", "content": response})
            return jsonify({"response": response})
        # while response["choices"][0]["finish_reason"] == "function_call":
        if response["choices"][0]["finish_reason"] == "function_call":
            if response["choices"][0]["message"]["function_call"]["name"] == "parse_report":
                function_response = parse_report(query)
                if isinstance(function_response, list):
                    final_response = function_response
                else:
                    final_response = "Apologies! I could not understand, Can you please rephrase and try again..."

            else:
                function_response = function_call(response)
                messages.append({
                    "role": "function",
                    "name": response["choices"][0]["message"]["function_call"]["name"],
                    "content": function_response
                })
                try:
                    response = ask_function_calling(
                        messages, self.function_descriptions)
                except Exception as e:
                    print("Function calling Error : ", e)
                    response = "Apologies! You have exceeded the maximum token limit of 4097. Please clear the chat and try again.\n"
                    self.chat_history.append(
                        {"role": "assistant", "content": response})
                    return jsonify({"response": response})
                if isinstance(function_response.split('\n')[-1], str) and isinstance(response.choices[0].message["content"], str):
                    response.choices[0].message["content"] = response.choices[0].message["content"] + \
                        '\n' + function_response.split('\n')[-1]
                    print(response.choices[0].message["content"])
                else:
                    print(response)
                    print(function_response.split('\n')[-1])
                    response.choices[0].message["content"] = "Sorry, I could not understand, Can you please rephrase and try again..."
                final_response = remove_last_source_pages(
                    response.choices[0].message["content"])
        else:
            final_response = response.choices[0].message["content"]

        self.chat_history += [{"role": "assistant",
                               "content": str(final_response)}]
        print("final_response:", final_response)
        return jsonify({"response": final_response})

    def get_response1(self, data):
        query = data["query"]
        print(query)
        self.chat_history += [{"role": "user", "content": str(query)}]
        print(query)
        # return jsonify({"response": query})


# reportString = {
#   "Exam Date": "02 GD",
#   "Age": "28yr 8m",
#   "LMP(EDD)": "09-30-2023",
#   "LMP": "12-24-2022",
#   "EstabDD": "09-30-2023",
#   "EDD": "09-30-2023",
#   "GA(EDD)": "27wéd",
#   "GA(LMP)": "27wéd",
#   "GA(EFW)": "29w2d",
#   "EDD(LMP)": "09-30-2023",
#   "AUA": "29w0d",
#   "EDD(AUA)": "09-22-2023",
#   "EFW in oz": "3ib 0oz (13499)",
#   "EFW in pctl": "71.72",
#   "Fetal HR avg value": "148 bpm",
#   "AFI cm value": "16.98 cm",
#   "AFI pctl value": "68.38",
#   "Gender": "Female",
#   "Fetal Position": "Breech",
#   "Fetal Head": "Not Found",
#   "Fetal Spine": "Not Found",
#   "Placenta Location": "Posterior",
#   "Placenta Grade": "2",
#   "3 V Cord": "Not Found",
#   "Cord Insertion": "Not Found",
#   "Amniotic Fluid": "Normal",
#   "Facial Profile": "Not Found",
#   "Diaphragm": "Not Found",
#   "Upper Extremity": "Not Found",
#   "Lower Extremity": "Not Found",
#   "Hands": "Not Found",
#   "Feet": "Not Found",
#   "Placenta Previa": "Not Found",
#   "Fetal Movements": "Positive",
#   "Fetal Tone": "Not Found",
#   "Fetal Breathing Move": "Not Found",
#   "Amniotic Fluid Volume": "Not Found",
#   "BPP Total out of 8": "Not Found",
#   "Q1 avg value in cm": "4.77 cm",
#   "Q2 avg value in cm": "3.41 cm",
#   "Q3 avg value in cm": "6.08 cm",
#   "Q4 avg value in cm": "2.72 cm",
#   "BPD value in cm": "6.98 cm",
#   "BPD value in pctl": "Not Found",
#   "HC value in cm": "26.62 cm",
#   "HC value in pctl": "Not Found",
#   "AC value in cm": "24.90 cm",
#   "AC value in pctl": "Not Found",
#   "FL value in cm": "5.62 cm",
#   "FL value in pctl": "Not Found",
#   "CRL value in cm": "Not Found",
#   "CRL value in pctl": "Not Found",
#   "YS value in cm": "Not Found",
#   "YS value in pctl": "Not Found",
#   "NT value in mm": "Not Found",
#   "NT value in pctl": "Not Found",
#   "CEREB avg value in cm": "Not Found",
#   "CEREB value in pctl": "Not Found",
#   "CM avg value in cm": "Not Found",
#   "CM value in pctl": "Not Found",
#   "NF avg value in cm": "Not Found",
#   "Lat Vent avg value in cm": "Not Found",
#   "FL/AC in %": "22.57%",
#   "FL/AC normal range": "(20.0~24.0%, >21w)",
#   "FL/BPD in %": "80.58%",
#   "FL/BPD normal range": "(71.0~87.0%, >23w)",
#   "FL/HC in %": "21.11%",
#   "FL/HC normal range": "(17.87~21.47%, 27w...)",
#   "HC/AC in %": "1.07",
#   "HC/AC normal range": "(1.05~1.22, 27w6d)",
#   "4 Chamber": "Not Found",
#   "Lt. Outflow Tract": "Not Found",
#   "Rt. Qutflow Tract": "Not Found",
#   "3 Vessel": "Not Found",
#   "Aortic Arch": "Not Found",
#   "Ductal Arch": "Not Found",
#   "Cardiac Rhythm": "Not Found",
#   "Lateral Ventricles": "Not Found",
#   "Cerebellum": "Not Found",
#   "Cist Magna": "Not Found",
#   "Cranium": "Not Found",
#   "Abdominal Wall": "Not Found",
#   "Spine": "Not Found",
#   "Stomach": "Not Found",
#   "Bladder": "Not Found",
#   "Lt. Kidney": "Not Found",
#   "Rt. Kidney": "Not Found",
#   "Cervix L avg value in cm": "Not Found",
#   "Rt. Overy L avg value in cm": "Not Found",
#   "Rt. Overy H avg value in cm": "Not Found",
#   "Rt. Overy W avg value in cm": "Not Found",
#   "Rt. Overy Vol. avg value in ml": "Not Found",
#   "Lt. Overy L avg value in cm": "Not Found",
#   "Lt. Overy H avg value in cm": "Not Found",
#   "Lt. Overy W avg value in cm": "Not Found",
#   "Lt. Overy Vol. avg value in ml": "Not Found",
#   "Comment": "NT AMA SLIUP @  12w4d (60.7MM) EDD 02/10/24 BY ULTRASOUND, SIZE C/W  DATES. YS SEEN. NT=1.4MM. NB SEEN. FHR= 155BPM. LT OV APPEARS WNL-SMALL FOLLICLE SEEN. RT OV NOT SEEN DUE TO GAS/BOWEL. ADNEXAE APPEARS WNL. POSSIBLE POST MYOMA MEASURING 3.1 X 2.7 X 2.7CM. POSSIBLE ANT SUBSEROSLAMYOMA MEASURNG 2.5 X 1.7 X 2.0CM. TA SCAN PERFORMED. AM RDMS"
# }

# negative_findings = get_negative_findings(reportString)
# print("------------final_______answer--------------")
# print(json_parser(negative_findings))
# print(get_guidelines("detailed guidelines for placenta previa with cpt reports"))