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
import time
import difflib
openai.api_key = os.environ.get("OPENAI_API_KEY")
import time
# from app import VectorDB
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

persist_directory = "./db"

# Create an instance of PDFUtils class
pdf_utils = PDFUtils(persist_directory)

# Call the initialize_qa_chain method to initialize the QA chain
# pdf_utils.initialize_qa_chain()

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

def extract_list_from_text(text):
    # Define a regular expression pattern to match the list inside square brackets
    pattern = r'\[([^[\]]*)\]'
    
    # Use the re.search function to find the list pattern in the text
    match = re.search(pattern, text)
    
    if match:
        # If a match is found, extract the content of the list and split it into individual elements
        list_content = match.group(1)
        extracted_list = [item.strip() for item in list_content.split(",")]
        return extracted_list
    else:
        # If no list is found, return None
        return None


def extract_content_in_braces(text):
    # Find the first opening brace from the left
    left_brace_index = text.find("[")
    
    # Find the first closing brace from the right
    right_brace_index = text.rfind("]")
    
    if left_brace_index != -1 and right_brace_index != -1 and left_brace_index < right_brace_index:
        # Extract the content within the curly braces
        content_between_braces = text[left_brace_index:right_brace_index+1].strip()
        return content_between_braces
    else:
        return None

def find_indices_of_difference(old_list, new_list):
    # Find the indices of elements in old_list that are not in new_list
    # indices_of_difference = [i for i, item in enumerate(old_list) if item.strip() not in new_list]
    indices_of_difference = []
    for i, item in enumerate(old_list):
        if item.strip() not in new_list:
            indices_of_difference.append(i)
    return indices_of_difference

def remove_elements_by_indices(indices, data):
    # Create a new dictionary with elements removed at specified indices
    updated_data = {key: value for i, (key, value) in enumerate(data.items()) if i not in indices}
    return updated_data

def remove_similar(abnormalities):
    old_list = [f"{key} {value}" for key, value in abnormalities.items()]
    try:
        output = get_completion([{"role": "system", "content": """Remove abnormalities from the provided list that mean the same and denote the same abnormality, if any (remove the latter element). Output only the final list and nothing else."""}, {
                                         "role": "user", "content": "Abnormality List: "+str(old_list)}])
        new_list = extract_content_in_braces(output)
        indices = find_indices_of_difference(old_list, new_list)
        abnormalities = remove_elements_by_indices(indices, abnormalities)
    except Exception as e:
        return abnormalities    
    print(abnormalities)
    return abnormalities

def remove_not_seen_values(abnormalities):
    # Create a new dictionary with elements where the value is not "Not seen"
    updated_abnormalities = {key: value for key, value in abnormalities.items() if str.lower(value) != "not seen"}
    return updated_abnormalities


def get_reports(abnormalities,negative_finding_keys,AUA):
    if negative_finding_keys is not None:
        print(negative_finding_keys) # debug here
        try:
            if any(negative_finding_keys):
                for key in negative_finding_keys:
                    if key not in abnormalities.keys():
                        abnormalities[key] = ""
        except Exception as e:
            print(e)
            pass
    print(abnormalities)
    print("above are all the possible abnormalities........................................................")
    abnormalities = remove_not_seen_values(abnormalities)
    print("\nNot seen value is removed...")
    print(abnormalities)

    start = time.time()
    if len(abnormalities.keys()) > 1:
        abnormalities = remove_similar(abnormalities)
    end = time.time()
    print("The time of execution for remove_similar which are below :",(end-start)," second")
    print(abnormalities)
    print("above are all the possible abnormalities list........................................................")
    
    if any(abnormalities):
        reports = "Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you.^_^"
        for key, value in abnormalities.items():
            # if "myoma" in str.lower(key):
            #     try:
            #         key = key.title().replace("Myoma","Myoma/ Uterine Fibroids in Pregnancy")
            #     except Exception as e:
            #         pass
            # if str.lower(value) == "not seen":
            #     continue
            print(str(key) + ": " + str(value))
            reports += f"{str(key)} : {str(value)}\n\n"
            query_context = f"{str(key)} : {str(value)}"
            if key == "Fetal Position":
                query = "I would like comprehensive guidelines for the confirm suspected abnormal" + str(key) + " "+str(value) + ".if there is any.\n"
            # elif "myoma" in str.lower(key):
            #     print("did myoma search")
            #     query = ""
            elif value == "yes":
                query = "I would like comprehensive guidelines for " + str(key) +".if there is any.\n"
            else:
                query = "I would like comprehensive guidelines for " + str(key) + " "+str(value) + ".if there is any.\n"
            
            start = time.time()
            result = pdf_utils.chat_with_pdf_q(query,AUA,query_context)
            end = time.time()
            print("The time of execution for get_reports :",(end-start)," second")
  
            if result == " ":
                pass 
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

# def get_guidelines(Question_string):
#     # que_prompt = """ related to obstetrical Replace abbreviations with full forms, except cpt/CPT """
#     # Question_string = get_completion([{"role": "system", "content": que_prompt},{"role": "user", "content": Question_string}])
#     print(Question_string)
#     try:
#         Question_string = get_completion([{"role": "system", "content": """Your task is to replace all obstetrical abbreviations in the given text with their full forms in (), except for "CPT(Current Procedural Terminology)". Please make sure to provide the expanded versions of the abbreviations wherever possible."""}, {
#                                          "role": "user", "content": str(Question_string)}])
#     except Exception as e:
#         print("Error: "+str(e))
#         return "Not found please try again."
#     print("Question : ", Question_string)
#     result = pdf_utils.chat_with_pdf_single_query(Question_string)
#     # result = get_answer_from_pdf(Question_string)
#     return str(result)

def get_abno_biometry(Report_string):
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


def get_abnormal_keys(json_data,report_string):

    abnormal_keys = []

    for key, value in json_data["abnormalities"].items():
        if value == "Abnormal":
            abnormal_keys.append(key)
        if "AFI cm value" in abnormal_keys and "AFI pctl value" in abnormal_keys:
            abnormal_keys.remove("AFI pctl value")
    
    # if "EFW in gram" in abnormal_keys or "EFW in pctl" in abnormal_keys:
    #     abnormal_keys.append("Known Macrosomia ≥90th percentile")
    #     if "EFW in pctl" in abnormal_keys:
    #         report_string["Known Macrosomia ≥90th percentile"] = "EFW "+str(report_string["EFW in pctl"])
    #     else:
    #         if "EFW in gram" in abnormal_keys:
    #             report_string["Known Macrosomia ≥90th percentile"] = "EFW "+str(report_string["EFW in gram"])

    if "EFW in pctl" in abnormal_keys:
        abnormal_keys.append("Known Macrosomia ≥90th percentile")
        if "EFW in pctl" in abnormal_keys:
            report_string["Known Macrosomia ≥90th percentile"] = "EFW is "+ str(report_string["EFW in pctl"])+" pctl"

    if "EFW in gram" in abnormal_keys:
        abnormal_keys.remove("EFW in gram")
        
    if "EFW in pctl" in abnormal_keys:
        abnormal_keys.remove("EFW in pctl")

    return abnormal_keys,str(report_string)

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
        print("may be any of the above missing....")
        try:
            if Age>34:
                ageFlag = True
            else :
                ageFlag = False
        except Exception as e:
            ageFlag = False

    print(f"final age flag is :{ageFlag}")
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
        if str(k) == "Age" and str(v) != "Not Found":
            try:
                Age = int(v.split("yr")[0])
            except Exception as e:
                try:
                    Age = int(str(v[:2]))
                except:
                    Age = None
    print(Age)
    print("Above is Age....................................................................................")

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
    print(f"sum_mvp is :{sum_mvp}, and flag is:{flag}")
    if len(final_ans) < 110:
        final_ans = ""
    return final_ans,flag,ageFlag

# prompt_comment = """You are expert in finding obstetric complications from ultrasound Reports Comment. Please review the ultrasound report and identify individual obstetric complications based on the provided values. If no values are provided then based on available information find the complication."""and identify individual obstetric complications based on the provided information. 
prompt_comment = """You are expert in finding obstetric complications from ultrasound Reports Comment. Only and only Identify each obstetric complications separately from ultrasound report. make sure you provide only and only true obstetric complications name from provided comment by thinking carefully. you will get a draft of ultrasound report comment."""

def get_negative_findings(reportString):
    try:
        history = [{"role": "system", "content": prompt_comment}]
        history += [{"role": "user", "content": str(reportString["Comment"])}] #"give me names of obstetric complications from below text\n"+ 
        try:
            # it will get me a json which contains possible abnormalities
            response3 = get_completion(history)
        except Exception as e:
            print("3Function calling Error : ", e)
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
            populate each <obstetric_complications> separately if report has any obstetric complications and return only JSON.
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
        return None
def get_AUA(Report_string):
    try:
        AUA_data = Report_string["AUA"]
        AUA = int(AUA_data.split("w")[0])
        if AUA < 50:
            pass
        else:
            AUA = AUA+"generate error"
    except Exception as e:
        print("AUA Not Found")
        AUA = None
    return AUA

def parse_report(Report_string):
    print("------------------- \nParsing Report \n------------------")
    history = [{"role": "system", "content": prompt.replace("<INSIGHTS_DATA>", get_insights(
        json.loads(Report_string), insightsAll))+"\n\nHere is the ultrasound Report\n"+Report_string}]
    AUA = get_AUA(json.loads(json_parser(Report_string)))
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

    start = time.time()
    try:
        # it will get me a json which contains possible abnormalities
        abnormalities = get_completion(history)
    except Exception as e:
        print("Function calling Error : ", e)
        abnormalities = "Oops! An issue with the OpenAI API. Can you please try again in a few minutes after clearing the chat."
        history.append({"role": "assistant", "content": abnormalities})
        return jsonify({"response": abnormalities})
    end = time.time()
    print("The time of execution for below abnormalities :",(end-start)," second")
    # abnormalities = response3
    print(abnormalities)
    print("above are intermediate things............")

    start = time.time()
    negative_finding_keys = get_negative_findings(json.loads(json_parser(Report_string)))
    end = time.time()
    print("The time of execution for get_negative_findings :",(end-start)," second")
    
    start = time.time()
    abnormal_keys,Report_string = get_abnormal_keys(json.loads(json_parser(abnormalities)),json.loads(json_parser(Report_string)))
    end = time.time()
    print("The time of execution for get_abnormal_keys :",(end-start)," second")

    Report_string = Report_string.replace("'", "\"")

    start = time.time()
    final_ans, mvp_flag,ageFlag = get_not_seen_mvp_edc(json.loads(json_parser(Report_string)))
    end = time.time()
    print("The time of execution for get_negative_findings :",(end-start)," second")

    # final_ans, mvp_flag,ageFlag = get_not_seen_mvp_edc(json.loads(json_parser(Report_string)))

    start = time.time()
    abnormalities = str(get_final_abnormalities(abnormal_keys, json.loads(json_parser(Report_string)),mvp_flag,ageFlag)["abnormalities"]).replace("'", "\"")
    end = time.time()
    print("The time of execution for get_final_abnormalities which are below :",(end-start)," second")

    print(abnormalities)
    print("Above are final Abnormalities....................]]]]]]]]]]]]]]]]]]]]")


    start = time.time()
    final_ans += get_reports(json.loads(abnormalities),negative_finding_keys,AUA)
    end = time.time()
    print("The time of execution for get_reports :",(end-start)," second")

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
        return "get guidelines function is commented"   #get_guidelines(Question_string)
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



def remove_duplicate(text):
    del1 = "Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you."
    del2 = "Please feel free to ask me any specific questions you have regarding the report. I'm here to help!😊"
    try:
        text.remove(del1)
        text.remove(del2)
    except Exception as e:
        pass
    new_text = []
    remaining_list = {}
    for i in range(len(text)):
        if len(text[i]) > 120:
            new_text.append(text[i][100:])
        else:
            remaining_list[str(i)] = text[i]



    def is_similar(a, b, threshold=0.45):
        """
        Determine if two strings are similar based on the difflib ratio.
        """
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        print(ratio)
        return ratio >= threshold

    def remove_duplicates(input_list):
        unique_list = []
        for item in input_list:
            is_duplicate = False
            for unique_item in unique_list:
                if is_similar(item, unique_item):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_list.append(item)
        return unique_list

    unique_text = remove_duplicates(new_text)

    final_answer = []
    for tex in text:
        for item in unique_text:
            if str(item[:19]) == str(tex[100:119]):
                print(item[:19])
                print(tex[100:119])
                final_answer.append(tex)

    if any(remaining_list):
        print("yes found in json")
        for key,value in remaining_list.items():
            final_answer.insert(int(key),value)
    final_answer.insert(0,del1)
    final_answer.append(del2)
    return final_answer

import re

def remove_duplicate_using_key_analysis(final_response):
    def get_key_analysis(final_response,key_json={}):
        # Use regular expressions to extract Key Analysis and Recommendations
        for i in range(len(final_response)):
            key_analysis_match = re.search(r'Key Analysis:(.*?)Recommendation:', final_response[i], re.DOTALL | re.IGNORECASE)
            key_analysis = key_analysis_match.group(1).strip() if key_analysis_match else ""
            if key_analysis != "":
                key_json[str(i)] = key_analysis

        return key_json

    def is_similar(a, b, threshold=0.45):
        """
        Determine if two strings are similar based on the difflib ratio.
        """
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        print(ratio)
        return ratio >= threshold

    def remove_duplicates(input_list):
        unique_list = []
        for item in input_list:
            is_duplicate = False
            for unique_item in unique_list:
                if is_similar(item, unique_item):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_list.append(item)
        return unique_list
    try:
        json_data = get_key_analysis(final_response)
        value_list = remove_duplicates(list(json_data.values()))

        # Initialize a list to store keys
        keys_not_in_list = []

        # Iterate through the dictionary and check if the value is not in the value_list
        for key, value in json_data.items():
            if value not in value_list:
                keys_not_in_list.append(key)
        for i in keys_not_in_list:
            final_response.pop(int(i))
    except Exception as e:
        pass
    
    return final_response


def remove_duplicate_using_Recommendation(final_response):
    def get_key_analysis(final_response,key_json={}):
        # Use regular expressions to extract Key Analysis and Recommendations
        for i in range(len(final_response)):
            try:
                recommendation = final_response[i].split("Recommendation:")[1]
            except Exception as e:
                continue
            # key_analysis_match = re.search(r'Recommendation:(.*?)', final_response[i], re.DOTALL | re.IGNORECASE)
            # key_analysis = key_analysis_match.group(1).strip() if key_analysis_match else ""
            if recommendation != "":
                key_json[str(i)] = recommendation
                print(recommendation)
                print("--------------")
        return key_json

    def is_similar(a, b, threshold=0.45):
        """
        Determine if two strings are similar based on the difflib ratio.
        """
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        print(ratio)
        return ratio >= threshold

    def remove_duplicates(input_list):
        unique_list = []
        for item in input_list:
            is_duplicate = False
            for unique_item in unique_list:
                if is_similar(item, unique_item):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_list.append(item)
        return unique_list
    try:
        json_data = get_key_analysis(final_response)
        value_list = remove_duplicates(list(json_data.values()))

        # Initialize a list to store keys
        keys_not_in_list = []

        # Iterate through the dictionary and check if the value is not in the value_list
        for key, value in json_data.items():
            if value not in value_list:
                keys_not_in_list.append(key)
        for i in keys_not_in_list:
            final_response.pop(int(i))
    except Exception as e:
        pass
    
    return final_response

def process_final_list(final_list):
    # Filter out strings that end with a colon and create a concatenated result
    result = "Negative finding detected. Below was included in the comments section:\n"
    result += '\n'.join([s.strip()[:-1] for s in final_list if s.strip().endswith(':')])
    result += "\n\nPlease schedule an ultrasound in 4 weeks to check again."

    # Modify final_list in place to remove the filtered strings
    final_list[:] = [s for s in final_list if not s.strip().endswith(':')]
    if len(result)>130:
        final_list.insert(-1,result)
    return final_list




class UltraBot():
    def __init__(self):
        self.chat_history = [
            {"role": "system", "content": prompt2},
            {"role": "user", "content": "hey"},
            {"role": "assistant", "content": "Hi! How can i hlep you today ?"}
        ]
        self.first_time = True
        self.function_descriptions = function_descriptions
        # self.db = VectorDB()

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


    # def get_response(self, data):
    #     time.sleep(3)
    #     return jsonify({"response": "done done done..."})

    def get_response(self, data,extra_time = None):
        start_time = time.time()
        function_response = None
        query = data["query"]
        self.chat_history += [{"role": "user", "content": str(query)}]
        messages = self.chat_history  # + [{"role": "user", "content": query}]

        # start = time.time()
        # try:
        #     response = ask_function_calling(
        #         messages, self.function_descriptions)
        # except Exception as e:
        #     print("1Function calling Error : ", e)
        #     response = "Apologies! You have exceeded the maximum token limit of 4097. Please clear the chat and try again.\n"
        #     self.chat_history.append(
        #         {"role": "assistant", "content": response})
        #     return jsonify({"response": response})
        # end = time.time()
        # print("The time of execution for ask_function_calling :",(end-start)," second")
        # while response["choices"][0]["finish_reason"] == "function_call":
        # if response["choices"][0]["finish_reason"] == "function_call":
        #     if response["choices"][0]["message"]["function_call"]["name"] == "parse_report":
        if True: # chnge in final stage
            if True: # change in final stage
                function_response = parse_report(query)
                if isinstance(function_response, list):
                    final_response = function_response
                    final_response = remove_duplicate(final_response)
                    final_response = remove_duplicate_using_key_analysis(final_response)
                    final_response = remove_duplicate_using_Recommendation(final_response)
                else:
                    final_response = ["Apologies! I could not understand, Can you please rephrase and try again...",]

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
                    print("2Function calling Error : ", e)
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
        print("below is final response")
        print(final_response)
        self.chat_history += [{"role": "assistant",
                               "content": str(final_response)}]
        print("final_response:", final_response)
        final_response = process_final_list(final_response)
        end_time = time.time()
        time_taken = "The time of execution :" + str((end_time-start_time)+extra_time)+" second"
        final_response.append(time_taken) 
        return jsonify({"response": final_response})

    def get_response1(self, data):
        query = data["query"]
        print(query)
        self.chat_history += [{"role": "user", "content": str(query)}]
        print(query)
        return jsonify({"response": query})

# AUA = None
# abnormalities = {"Socio-Demographic Risk Factors (maternal age)": "Age ≥ 35"}
# # # abnormalities = {'Fetal Position': 'Breech',}
# # abnormalities = {"Fetal Position": "Breech", "Placenta Previa": "Yes"}
# negative_finding_keys = ['Subserosal myoma', 'Gas/Bowel obstruction'] 
# # negative_finding_keys = {'Fetal Position': 'Breech', 'Placenta Previa': 'Yes', 'EIF (echogenic intracardiac focus) seen in the left ventricle': '', 'Anterior placenta grade 2 partial previa, covering the 10S by 1.5cm': ''} 
# # # negative_finding_keys = {'Socio-Demographic Risk Factors (maternal age)': 'Age ≥ 35', 'SLIUP (Suboptimal Lie of the Uterus)': '', 'Gas/Bowel interference in visualizing the right ovary': '', 'Possible post myoma (fibroid) measuring 3.1 x 2.7 x 2.7 cm': '', 'Possible anterior subserosal myoma measuring 2.5 x 1.7 x 2.0 cm': ''}
# get_reports(abnormalities,negative_finding_keys,AUA)

# ultrabot = UltraBot()
# json_data_pure = {"EFW in pctl": "71.72", "Fetal HR avg value": "148 bpm", "AFI cm value": "16.98 cm", "AFI pctl value": "68.38", "Gender": "Female", "Fetal Position": "Breech", "Placenta Location": "Posterior", "Placenta Grade": "2", "Amniotic Fluid": "Normal", "Fetal Movements": "Single breech female fetus with positive fetal movement.", "Q1 avg value in cm": "4.77 cm", "Q2 avg value in cm": "3.41 cm", "Q3 avg value in cm": "6.08 cm", "Q4 avg value in cm": "2.72 cm", "BPD value in cm": "6.98 cm", "HC value in cm": "26.62 cm", "AC value in cm": "24.90 cm", "FL value in cm": "5.62 cm", "FL/AC in %": "22.57%", "FL/AC normal range": "(20.0~24.0%, >21w)", "FL/BPD in %": "80.58%", "FL/BPD normal range": "(71.0~87.0%, >23w)", "FL/HC in %": "21.11%", "FL/HC normal range": "(17.87~21.47%, 27w...)", "HC/AC in %": "1.07", "HC/AC normal range": "( 1.05~1.22, 27w6d)", "Comment": "\n\\r\\n\\r\\n\\r\\n\\r\\n\\r\\n\\r\\n                                                                                                                 07-07-2023 09:50 am\\r\\n\\r\\n\\x0c                                                  ULTRASOUND REPORT\\r\\n\\r\\n                                            Ultrasound Report\\r\\n\\r\\n      GROWTH\\r\\n\\r\\n         Single breech female fetus with positive fetal movement.\\r\\n         FHR=154bpm with normal cardiac rhythm.\\r\\n        EFW=3#00z / 72nd%\\r\\n        AFI=17cm\\r\\n          Posterior placenta grade 2  previa seen.\\r\\n\\r\\n       K"}
# data = {'query': str(json_data_pure), type: ''}
# print(get_negative_findings(json_data_pure))



# final_response = ['Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you.', 'Fetal Position : Breech\n\nKey Analysis: Fetal presentation should be assessed by abdominal palpation (Leopold’s) at 36 weeks or later, when presentation is likely to influence the plans for the birth. Routine assessment of presentation by abdominal palpation before 36 weeks is not always accurate. Suspected fetal malpresentation should be confirmed by an ultrasound assessment. An ultrasound can be performed at ≥36 weeks gestation to determine fetal position to allow for external cephalic version. Ultrasound to determine fetal position is not necessary prior to 36 weeks gestation unless delivery is imminent.\n\nRecommendation:\n- To confirm suspected abnormal fetal position or presentation (transverse or breech presentation) at ≥36 weeks gestation, report one of the following:\n  - CPT® 76805 (plus CPT® 76810 for each additional fetus) when complete anatomy scan has not yet been performed in the pregnancy\n  - CPT® 76815 for limited ultrasound to check fetal position\n  - CPT® 76816 if version is being considered and/or for delivery planning', 'confirmed diagnosis of polyhydramnios : maximum vertical pocket(MVP) ≥8cm.\n\nKey Analysis: Polyhydramnios is confirmed when the maximum vertical pocket (MVP) is ≥8cm.\nRecommendation:\n- Perform a Detailed Fetal Anatomy Scan (CPT® 76811) at diagnosis, if not previously performed.\n- Perform a follow-up ultrasound (CPT® 76816) every 3-4 weeks for mild polyhydramnios (AFI 24-29.9cm or MVP 8-9.9cm).\n- Perform a follow-up ultrasound (CPT® 76816) every 2 weeks for severe polyhydramnios (AFI ≥30cm or MVP ≥10cm).\n- Perform antepartum fetal surveillance with a quick look for AFI check (CPT® 76815) weekly starting at ≥23 weeks.\n- Perform a Biophysical Profile (BPP) or modified BPP (CPT® 76818, CPT® 76819, or CPT® 76815) for AFI with NST starting at 26 weeks.\n- Perform umbilical artery (UA) Doppler (CPT® 76820) weekly starting at the time of diagnosis if ≥23 weeks.', 'Breech presentation : \n\nKey Analysis: Breech presentation refers to the position of the fetus in which the buttocks or feet are positioned to be delivered first instead of the head. It is important to assess fetal presentation to determine the appropriate management and delivery plan.\n\nRecommendation:\n- To confirm suspected breech presentation at ≥36 weeks gestation, the following CPT reports can be considered:\n  - CPT® 76805 (plus CPT® 76810 for each additional fetus) if a complete anatomy scan has not yet been performed in the pregnancy.\n  - CPT® 76815 for a limited ultrasound to check fetal position.\n  - CPT® 76816 if version (manually turning the fetus) is being considered and/or for delivery planning.\n\nNote: No specific CPT reports are mentioned in the context for breech presentation.', 'Placenta previa : \n\nKey Analysis: Placenta previa is characterized by the placental edge covering the internal cervical os or being less than 2 cm away from it. \nRecommendation:\n- For suspected placenta previa, the following ultrasound options can be performed:\n  - CPT® 76805 [plus CPT® 76810 for each additional fetus] and/or CPT® 76817 if a complete fetal anatomic scan has not yet been performed during this pregnancy, with or without CPT® 93976 (limited duplex scan)\n  - CPT® 76815 for limited ultrasound and/or CPT® 76817 with or without CPT® 93976 (limited duplex scan)\n  - CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817 for a transvaginal ultrasound with or without CPT® 93976 (limited duplex scan)\n- For known placenta previa or low lying placenta (placental edge <2 cm from internal os):\n  - One routine follow-up ultrasound can be performed in the 3rd trimester (CPT® 76815 or CPT® 76816 and/or CPT® 76817)\n  - If placenta previa or low lying placenta is still present, one follow-up ultrasound (CPT® 76815 or CPT® 76816 and/or CPT® 76817) can be performed in 3-4 weeks\n  - If persistent placenta previa (placental edge covers the internal cervical os), BPP (CPT® 76818/CPT® 76819 or modified BPP (CPT® 76815) can be performed weekly, starting at 32 weeks\n  - Follow-up ultrasound can be performed at any time if bleeding occurs, using BPP (CPT® 76818 or CPT® 76819) or CPT® 76815 or CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817', "Please feel free to ask me any specific questions you have regarding the report. I'm here to help!😊"]
# print(remove_duplicate_using_Recommendation(final_response))

# reportString = {
#  'Comment': '\\r\\n\\r\\n\\r\\n\\r\\n                                                                                                                  08-07-2023 10:05 am\\r\\n\\r\\n\\x0c                                                  ULTRASOUND REPORT\\r\\n\\r\\n                                            Ultrasound Report\\r\\n\\r\\n       BPP\\r\\n\\r\\n          Single vertex male fetus.\\r\\n         FHR=147bpm with normal cardiac rhythm.\\r\\n        EFW=9#20z / 98th%\\r\\n        AFI=10.4cm\\r\\n         Fundal placenta grade 2\\r\\n        BPP8/8\\r\\n\\r\\n       K'   
# }
# print(get_negative_findings(reportString))

# query = 'I would like comprehensive guidelines for the Socio-Demographic Risk Factors (maternal age) Age ≥ 35 along with CPT reports.if there is any.\n'
# AUA = 15
# print(pdf_utils.chat_with_pdf_q(query,AUA))