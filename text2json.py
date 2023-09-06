from pdf2text import convert2text
# from utils import convert2text
import openai
from dotenv import load_dotenv
load_dotenv()
import os
from langchain.embeddings import OpenAIEmbeddings


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


def text_to_json(report_text):
    post_prompt_json = """
    Generate a flat JSON from the provided text that encompasses variables which are present in above text and below list.
    Strictly include those which are present in above text. think step by step...

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
EFW in oz
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

Fetal Movements 
Fetal Tone
Fetal Breathing Move
Amniotic Fluid Volume
Total out of 8

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

Comments
"""
    # print(str(report_text,'UTF-8'))
    # history = [{"role": "user", "content": str(report_text,'UTF-8') + post_prompt_json}] # when report_text is dynamic
    history = [{"role": "user", "content": report_text + post_prompt_json}] # when report text is static
    # history = [{"role": "user", "content": "can you formate it properly as csv\n"+str(report_text,'UTF-8')}]
    report_csv = get_completion(history)
    return report_csv
    



# report_text = """                                                 ULTRASOUND REPORT

#                                            Ultrasound Report

#         ,
#      Name —             ID                Exam. Date    07-12-2023
#          Gender         Female              BirthDate    p——           Age              34yr Tm
#             Institute           AZ WOMEN'S SPECI...  Diag. Physicia n                       Ref. Physician       HETAL SHAH,...
#          Sonographer    KS.RDMS
#          Description       BPP
#           .
#     [OB]
#         LMP(EDD) 10-08-2022            EstabDD 07-15-2023                EDD 07-15-2023
#         GA(EDD) 39w4d            Pctl. Crit... EstabDD
#         General                              AVG                2        3
#                                                                                          no
#         Fetal HR                            |   S42      142                         bpm

#         AFI                           Last       1                  3                          Pctl.
#                                                                                   | 2
#        Q1                        0.00     0.00                     cm     Avg.
#       Q2                     4.69    4.69                    cm     Avg.
#        Q3                      5.61     5.61                    cm     Avg.
#       Q4                     6.83    6.83                   cm     Avg.
#         AFI                          17.13    17.13                        cm               79.14
#          Fetal Description                       RE       ERO   RR 1 | | |       Value
#          Gender                                             Female
#          Fetal Position                                                 Transverse
#          Placenta Location                                           Anterior
#          Placenta Grade                                               2
#          Amniotic Fluid                                                Normal
#          AC                                                            8.2 pctl
#          Biophysical Profile
#         Fetal Movements                  2          Fetal Breathing Move...           2
#          Fetal Tone                          2           Amniotic Fluid Volume              2
#          Total                                8

#        Comment
#        BPP

#          Single transverse maternal right female fetus.
#         FHR=142bpm with normal cardiac rhythm.
#         AFI=17.1cm
#          Anterior placenta grade 2
#         BPP8/8

#        KS.RDMS




#                                                                                                                   07-12-2023 03:45 pm
# """

# history += [{"role": "assistant", "content": report_csv}]

# history += [{"role": "user", "content": post_prompt_csv}]
# report_json = get_completion(history)
# print(report_json)


