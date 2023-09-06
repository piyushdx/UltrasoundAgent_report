
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from config import config, environment, ip_config
import re
from ultrabot import UltraBot
from ultrabot import parse_report
from utils import convert2text
import os
from text2json import *
app = Flask(__name__)
CORS(app, support_credentials=True)

ultrabot = UltraBot()



@app.route('/UltraBot_clear_cache', methods=['POST'])
@cross_origin(supports_credentials=True)
def UltraBot_clear_cache():
    return ultrabot.clear_cache(request.get_json())

@app.route('/UltraBot_get_response', methods=['POST'])
@cross_origin(supports_credentials=True)
def UltraBot_get_response():
    return ultrabot.get_response(request.get_json())


# @app.route('/convert', methods=['POST'])
# @cross_origin(supports_credentials=True)
# def convert():
#     print("hiiiii")
#     pdf_file = request.files['pdf']
#     print(type(pdf_file))
#     pdf_file.save("temp.pdf")

#     print("in")
#     convert2text(request.files['pdf'])

@app.route("/convert", methods=["POST"])
@cross_origin(supports_credentials=True)
def upload_file():
    uploaded_file = request.files["pdf"]
    if uploaded_file:
        # Do something with the uploaded file (e.g., save it)
        uploaded_file.save("ChatBotUI/static/pdf/uploaded.pdf")
        print("file is saved")
        # report_text = convert2text(request.files['pdf'])
        
#         report_text = """
#                                                   ULTRASOUND REPORT

#                                             Ultrasound Report
#  CEDName       8. Exam. Date 08-29-2023
#          Gender         Female               BirthDate                       Age              38yr Om
#             institute           AZ WOMEN'S SPECI...  Diag. Physician SHAH                Ref. Physician       HETAL SHAH,...
#          Sonographer    KS.RDMS
#           (Description        BPP
#     [OB]
#         LMP(EDD) 12-01-2022            EstabDD 09-07-2023                EDD 09-07-2023
#         GA(EDD) 38wbd            Pctl. Crit... EstabDD
#         General                              Avg.       1        2
#         Fetal HR                            |   136      136                         bpm

#         AFI                           Last       1        2        3                         Pctl.
#        Q1                       4.50     4.50                     cm     Avg.
#       Q2                      0.00    0.00                    cm    Avg.
#       Q3                     4.09    4.09                    cm    Avg.
#       Q4                     0.00    0.00                   cm    Avg.
#         AFI                           8.59     8.59                         cm               10.62
#          Fetal Description                                               Value
#        Gender                                              Male
#          Fetal Position                                                   Vertex
#         Placenta Location                                          Posterior
#         Placenta Grade                                               2
#          Amniotic Fluid                                                Normal
#          Biophysical Profile
#         Fetal Movements                             Fetal Breathing Move...           2
#         Fetal Tone                                     Amniotic Fluid Volume              2
#          Total                                ONDN

#       Comment
#        BPP

#           Single vertex male fetus.
#         FHR=136bpm with normal cardiac rhythm.
#         AFI=8.6cm
#          Posterior placenta grade 2
#         BPP8/8

#        KS.RDMS





#                                                                                                                   08-29-2023 01:03 pm
# """

#         report_text = """                                                 ULTRASOUND REPORT

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
#          Fetal Position                                                 Shoulder presentation
#          Placenta Location                                           Low-lying
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
        
        report_text = """
                                                       ULTRASOUND REPORT

                                     AZ WOMEN'S SPECIALISTS
             Name        GED
                                     FN Exam. Date     08-02-2023
          Gender        Female            BirthDate                                  43yr10m
                                 ~                                                                  Age
                 Institute           AZ WOMEN'S SPECI...  Ref. Physician   DR.HETAL SHAH    Sonographer        AM RDMS
              Description       NT AMA
        [OB]
                   LMP(EDD) 05-11-2023                         EDD 02-15-2024                     GA(EDD) 11wéd
                    AUA 12w4d                    EDD(AUA) 02-10-2024              Pctl. Criteria EstabDD
               Fetal Biometry        Avg.       1        2        3                      GA                    Pctl.
            CRL                6.07    6.06    6.07           cm         12wad+7d    Hadlock   97.72*   Rempen
             YS               |  0.49     0.49                   cm

               Fetal Cranium         Avg.       1        2        3                      GA                   Pctl.
             NT               |  1.61     1.79     1.43           mm                              23.01    Yagel
              General                                       Avq.         1          2          3
               Fetal HR                                          155         155                               bpm

            Comment
            NT AMA

             SLIUP @  12w4d (60.7MM) EDD 02/10/24 BY ULTRASOUND, SIZE C/W  DATES. YS SEEN. NT=1.4MM. NB SEEN.
              FHR= 155BPM.
             LT OV APPEARS WNL-SMALL FOLLICLE SEEN. RT OV NOT SEEN DUE TO GAS/BOWEL.
             ADNEXAE APPEARS WNL.
              POSSIBLE POST MYOMA MEASURING 3.1 X 2.7 X 2.7CM. POSSIBLE ANT SUBSEROSLAMYOMA MEASURNG 2.5 X 1.7
                X 2.0CM.

             TA SCAN PERFORMED.

           AM RDMS

           [ Gynecology ]
                       LMP 05-11-2023

                Lt. Ovary                                            Avg.          1            2           3
               Lt Ovary L                                       3.98        3.98                               cm
                Lt. Ovary H                                          2.40        2.40                                 cm
               Lt. Ovary W                                       3.68        3.68                                cm
                 Lt. Ovary Vol.                                        18.47        18.47                                  ml
          Images

                            Ana                  EhaTANRE EE                                        AZ WOMENS SPECIALISTS AF 12 08-02-2023
                            LATE  ET    i 1]      AT      aaa BA                                                 FN    aTISERIE










                                                                                                                       08-02-2023 02:32 pm

                                                       ULTRASOUND REPORT

                                     AZ WOMEN'S SPECIALISTS

                                                                                                                 WOMANS SPECALSTS MF 11 0002.2023
                                                                                                                             LLL ERTS TET

































                                                                                                                       08-02-2023 02:32 pm


"""
        
        json_data = text_to_json(report_text)
        # final_response = parse_report(json_data)
        print(json_data)
        print("---------------------------")
        
        # print(final_response)
        # return jsonify({"message": "File uploaded successfully."}), 200
        # return jsonify({"response": final_response})
        data = {'query': json_data, type: ''}
        return ultrabot.get_response(data)

    else:
        return jsonify({"message": "No file uploaded."}), 400

if __name__ == '__main__':
    IP = ip_config[environment]
    response_port = config['BotApplication']['Backend']  # response API
    app.run(host='0.0.0.0', port=response_port)

