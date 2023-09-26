from pdf2text import convert2text
# from utils import convert2text
import openai
from dotenv import load_dotenv
load_dotenv()
import os
from langchain.embeddings import OpenAIEmbeddings
import re
from ultrabot import json_parser
import json

embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4 # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def remove_bad_escaped_characters(input_string):
    # Define a regular expression pattern to match bad escaped characters
    pattern = re.compile(r'\\[^\w\s]')  # Matches any backslash followed by a non-alphanumeric character

    # Use sub() function to replace matched patterns with an empty string
    cleaned_string = re.sub(pattern, '', input_string)

    return cleaned_string
import string
def remove_bad_characters(input_text):
    # Define the set of printable characters
    # printable_chars = set(string.printable)
    # Filter out characters that are not in the set of printable characters
    # cleaned_text = ''.join(char for char in input_text if char in printable_chars)
    cleaned_text =  ''.join(char for char in input_text if char.isprintable())

# Remove extra whitespace and normalize spaces
    # cleaned_text = ' '.join(cleaned_text.split())
    print(cleaned_text)

    return cleaned_text

def text_to_json(report_text):
    post_prompt_json = """
Generate a flat JSON from the provided text that encompasses variables that are present in the below list. Include parameters that have a respective value in the above ultrasound report text. If a parameter doesn't have a value in the above ultrasound report text, it should compulsory appear in the json with a "Not Found" value.

Exam Date
Age
LMP(EDD)
LMP
EstabDD
EDD
GA(EDD)
GA(LMP)
GA(EFW)
EDD(LMP)
AUA
EDD(AUA)
EFW in gram
EFW in pctl

Fetal HR avg value
AFI cm value
AFI pctl value

Gender
Fetal Position 
Fetal Head
Fetal Spine
Placenta Location
Placenta Grade
3 V  Cord
Cord Insertion
Amniotic Fluid
Facial Profile
Diaphragm
Upper Extremity
Lower Extremity
Hands
Feet
Placenta Previa

Fetal Movements 
Fetal Tone
Fetal Breathing Move
Amniotic Fluid Volume
BPP Total out of 8

Q1 avg value in cm
Q2 avg value in cm
Q3 avg value in cm
Q4 avg value in cm

BPD value in cm
BPD value in pctl
HC value in cm
HC value in pctl
AC value in cm
AC value in pctl
FL value in cm
FL value in pctl
CRL value in cm
CRL value in pctl
YS value in cm
YS value in pctl
NT value in mm
NT value in pctl

CEREB avg value in cm
CEREB value in pctl
CM avg value in cm
CM value in pctl
NF avg value in cm
Lat Vent avg value in cm

FL/AC in %
FL/AC normal range
FL/BPD in %
FL/BPD normal range
FL/HC in %
FL/HC normal range
HC/AC in %
HC/AC normal range

4 Chamber
Lt. Outflow Tract
Rt. Qutflow Tract
3 Vessel
Aortic Arch
Ductal Arch
Cardiac Rhythm

Lateral Ventricles
Cerebellum
Cist Magna
Cranium

Abdominal Wall
Spine
Stomach
Bladder
Lt. Kidney
Rt. Kidney 

Cervix L avg value in cm

Rt. Overy L avg value in cm
Rt. Overy H avg value in cm
Rt. Overy W avg value in cm

Rt. Overy Vol. avg value in ml 

Lt. Overy L avg value in cm
Lt. Overy H avg value in cm
Lt. Overy W avg value in cm

Lt. Overy Vol. avg value in ml  

"""
    result = re.search(r'Comment(.*?)(?:RDMS|$)', report_text, re.DOTALL)

    if result:
        comment = result.group(1).strip()
    else:
        comment = "Not Found"
    cleaned_string = remove_bad_characters(comment)
    print(cleaned_string)
    print("above is comment...")
    # consider all the data till the word KS RDMS OR AM RDMS foundas a comment Bad escaped character [, '\n', , ]
    # post_prompt_json = "Create a json of above text. Only add parameters which hat respective values in the above file. "
    # history = [{"role": "user", "content": str(report_text,'UTF-8') + post_prompt_json}] # when report_text is dynamic
    history = [{"role": "user", "content": report_text + post_prompt_json}] # when report text is static
    jsonReport = get_completion(history)
    print(jsonReport)
    print("above is json report from get completion")
    jsonReport = json.loads(json_parser(jsonReport))
    jsonReport["Comment"] = str(comment)
    return str(jsonReport).replace("'", "\"")

