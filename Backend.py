
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



@app.route('/UltraBot_clear_cache')
@cross_origin(supports_credentials=True)
def UltraBot_clear_cache():
    return ultrabot.clear_cache()

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
        
#         report_text = """
#                                                        ULTRASOUND REPORT

#                                      AZ WOMEN'S SPECIALISTS
#              Name        GED
#                                      FN Exam. Date     08-02-2023
#           Gender        Female            BirthDate                                  43yr10m
#                                  ~                                                                  Age
#                  Institute           AZ WOMEN'S SPECI...  Ref. Physician   DR.HETAL SHAH    Sonographer        AM RDMS
#               Description       NT AMA
#         [OB]
#                    LMP(EDD) 05-11-2023                         EDD 02-15-2024                     GA(EDD) 11wéd
#                     AUA 12w4d                    EDD(AUA) 02-10-2024              Pctl. Criteria EstabDD
#                Fetal Biometry        Avg.       1        2        3                      GA                    Pctl.
#             CRL                6.07    6.06    6.07           cm         12wad+7d    Hadlock   97.72*   Rempen
#              YS               |  0.49     0.49                   cm

#                Fetal Cranium         Avg.       1        2        3                      GA                   Pctl.
#              NT               |  1.61     1.79     1.43           mm                              23.01    Yagel
#               General                                       Avq.         1          2          3
#                Fetal HR                                          155         155                               bpm

#             Comment
#             NT AMA

#              SLIUP @  12w4d (60.7MM) EDD 02/10/24 BY ULTRASOUND, SIZE C/W  DATES. YS SEEN. NT=1.4MM. NB SEEN.
#               FHR= 155BPM.
#              LT OV APPEARS WNL-SMALL FOLLICLE SEEN. RT OV NOT SEEN DUE TO GAS/BOWEL.
#              ADNEXAE APPEARS WNL.
#               POSSIBLE POST MYOMA MEASURING 3.1 X 2.7 X 2.7CM. POSSIBLE ANT SUBSEROSLAMYOMA MEASURNG 2.5 X 1.7
#                 X 2.0CM.

#              TA SCAN PERFORMED.

#            AM RDMS

#            [ Gynecology ]
#                        LMP 05-11-2023

#                 Lt. Ovary                                            Avg.          1            2           3
#                Lt Ovary L                                       3.98        3.98                               cm
#                 Lt. Ovary H                                          2.40        2.40                                 cm
#                Lt. Ovary W                                       3.68        3.68                                cm
#                  Lt. Ovary Vol.                                        18.47        18.47                                  ml
#           Images

#                             Ana                  EhaTANRE EE                                        AZ WOMENS SPECIALISTS AF 12 08-02-2023
#                             LATE  ET    i 1]      AT      aaa BA                                                 FN    aTISERIE










#                                                                                                                        08-02-2023 02:32 pm

#                                                        ULTRASOUND REPORT

#                                      AZ WOMEN'S SPECIALISTS

#                                                                                                                  WOMANS SPECALSTS MF 11 0002.2023
#                                                                                                                              LLL ERTS TET

































#                                                                                                                        08-02-2023 02:32 pm

# 
# """
        
        # report_text = """ULTRASOUND REPORT\r\n\r\n                                 AZ WOMEN'S SPECIALISTS\r\n       Name        GED         ID                          Exam. Date       08-02-2023\r\n        Gender         Female              BirthDate                      Age              16yr Om\r\n           institute            AZ WOMEN'S SPECI...  Ref. Physician DR.HETAL SHAH    Sonographer        AM RDMS\r\n          Description       FETAL ANATOMY\r\n    [OB]\r\n             LMP(EDD) 03-19-2023                         EDD 12-24-2023                     GA(EDD) 19w3d\r\n               AUA 18w5d                    EDD(AUA) 12-29-2023                     EFW 0lb 90z (259g)\r\n          EFW Author Hadlock4(BPD,HC,A...       Pctl.(EFW) 16.32                    Pctl. Criteria EstabDD\r\n        Fetal Biometry        Avg.      1        2        3                     GA                   Pctl.\r\n       BPD              4.35    4.35                 cm        19w1dt12d   Hadlock   38.49   Hadlock\r\n        HC                15.16    15.16                  cm        18w1d+10d    Hadlock   3.63   Hadlock\r\n       AC               13.51    13.51                 cm        19w0dt14d   Hadlock   29.97   Hadlock\r\n         FL                    2.86     2.56     2.86             cm   Last    18w5d+13d    Hadlock    21.00   Hadlock\r\n         Fetal Cranium         Avg.       1        2        3                      GA                   Pctl.\r\n       CEREB             1.92    1.92                 cm        18w5d+13d     Hill     33.21   Nicolai...\r\n       cm               0.46    0.46                cm                          39.72  Nicolai...\r\n        NF                  0.38     0.38                    cm  Max\r\n         Lat Vent               0.67      0.67                       cm\r\n         General                                       Avg.         1                     3\r\n         Fetal HR                                          150         150                               bpm\r\n          Ratio                Value                        Normal Range\r\n         FL/AC              21.18        %          (20.0~24.0%, >21w)\r\n        FL/BPD            65.77       %         {71.0~87.0%, >23w)\r\n        FL/HC             18.87        %        (15.13~20.21%, 19w3d)\r\n        HC/AC             1.12                  (1.09~1.26, 19w3d)\r\n\r\n          Fetal Description                                                               Value\r\n        Gender                                                         Seen\r\n          Fetal Position                                                                   Breech\r\n          Fetal Spine                                                                 Anterior\r\n         Placenta Location                                                        Posterior\r\n         Placenta Grade                                                            1\r\n         Placenta Previa                                                              No\r\n        3V Cord                                                            Yes\r\n         Amniotic Fluid                                                             Normal\r\n          Facial Profile                                                                    Not seen\r\n        Diaphragm                                                         Seen\r\n         Upper Extremity                                                           Seen\r\n         Lower Extremity                                                         Seen\r\n        Hands                                                           Seen\r\n         Feet                                                                  Not seen\r\n\r\n          Fetal Heart                                                                   Value\r\n        4 Chamber                                                      Not seen\r\n          Lt. Outflow Tract                                                              Not seen\r\n          Rt. Outflow Tract                                                             Not seen\r\n\r\n          Fetal Brain                                                                    Value\r\n          Lateral Ventricles                                                              Seen\r\n        Cerebellum                                                          Seen\r\n         Cist Magna                                                               Seen\r\n        Cranium                                                           Seen\r\n\r\n        Fetal Abdomen                                                       Value\r\n        Abdominal Wall                                                       Seen\r\n         Spine                                                                Not seen\r\n        Stomach                                                        Seen\r\n\r\n\r\n                                                                                                                  08-02-2023 11:04 am\r\n\r\n\x0c                                                 ULTRASOUND REPORT\r\n\r\n                                 AZ WOMEN'S SPECIALISTS\r\n\r\n        Fetal Abdomen                                                      Value\r\n         Bladder                                                               Seen\r\n          Lt. Kidney                                                                     Seen\r\n         Rt Kidney                                                            Seen\r\n\r\n         Maternal Others                                 Avg.         1           2           3\r\n         Cervix L                                          3.27        3.22        3.29        3.31         cm\r\n\r\n       Comment\r\n        FETAL ANATOMY G1 TEEN PREGNANCY\r\n\r\n         SLIUP @ 18WSD EDD 12/29/23 BY ULTRASOUND, SIZE C/W DATES, OVERALL 16% (259G OLB 902). BREECH.\r\n        FHR=150BPM. GOOD FETAL MOVEMENT SEEN. UNABLE TO OBTAIN PROFILE, N/L\r\n                                                                                 , CARDIAC, SPINE, FEET, LOWER\r\n        EXT VIEWS DUE TO FETAL POSITION. ALL OTHER ANATOMY APPEARS WNL. POST FUNDAL PL- NO PREVIA.\r\n         CX=3.2CM.\r\n\r\n        TA & TV SCAN PERFORMED.\r\n\r\n       AM RDMS\r\n     Images\r\n\r\n                       [I=                   EaTELERR)\r\n                LIE Lanal          ae   EE LU RR  SEE\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n                                                                                                                 08-02-2023 11:04 am\r\n\r\n\x0c"""

        report_text_85978 = """
                                                  ULTRASOUND REPORT

                                           Ultrasound Report

       7
                                                                               Exam. Date        08-07-2023
        Gender                           Binhpate                   Age             251m
                       =~    ~~ Female                            Institute           AZ WOMEN'S SPECI... Diag. Physician SHAH                Ref. Physician     "HETAL SHAH...
         Sonographer    KS.RDMS
          Description       BPP
           w
    [OB]
        LMP(EDD) 11-21-2022            EstabDD 08-28-2023                EDD 08-28-2023
        GA(EDD) 37w0d                  AUA 40w0d             EDD(AUA) 08-07-2023
              EFW 9lb 20z (41479)      EFW Aut... Hadlock2(BPD,...   Pctl.(EFW) 98.40"
         Pctl. Crit... EstabDD

         Fetal Biomet      Avg.     1       2       3                  GA                Pctl.
      BPD          9.73   9.73             cm     39wé6d+22d  Hadl... 99.27% Hadl...
      HC           36.08  36.08                       ek
                                            cm                Hadl... 99.69% Hadl...
      AC           37.31  37.31             cm     41w2d+21d  Hadl... 99.98* Hadl...
       FL              7.62   7.62                cm      39w0d+22d  Hadl...  90.18  Hadi...

        General                               Avg.       1        2        3
        Fetal HR                            |   147      147                         bpm

        AFI                           Last       1         2        3                          Pctl.
       Q1                        5.53     5.53                     cm     Avg.
       Q2                      0.00    0.00                    cm     Avg.
       Q3                      3.52    3.52                    cm     Avg.
      Q4                      1.35    1.35                    cm     Avg.
        AFI                           10.40     10.40                         cm               19.76

         Ratio           Value      Il       | 8 Normal Range  1
       FL/AC         20.43     %      (20.0~24.0%, >21w)
       FL/BPD       78.32     %     (71.0~87.0%, >23w)
       FL/HC         21.13     %    (19.90~23.50%, 37w...
       HC/AC        0.97            (0.92~1.05, 37w0d)
         Fetal Description                                               Value
                                                                                             AN  1
       Gender                                              Male
         Fetal Position                                                   Vertex
        Placenta Location                                           Fundal
        Placenta Grade                                              2
         Amniotic Fluid                                                Normal
         Biophysical Profile
        Fetal Movements                  nN          Fetal Breathing Move...           2
        Fetal Tone                                     Amniotic Fluid Volume              2
         Total                                oo

      Comment



                                                                                                                  08-07-2023 10:05 am

                                                  ULTRASOUND REPORT

                                            Ultrasound Report

       BPP

          Single vertex male fetus.
         FHR=147bpm with normal cardiac rhythm.
        EFW=9#20z / 98th%
        AFI=10.4cm
         Fundal placenta grade 2
        BPP8/8

       KS.RDMS





















                                                                                                                  08-07-2023 10:05 am


"""
         
#         report_text_53152 = """
#                                                        ULTRASOUND REPORT

#                                      AZ WOMEN'S SPECIALISTS
#              Name        GED
#                                      FN Exam. Date     08-02-2023
#           Gender        Female            BirthDate                                  43yr10m
#                                  ~                                                                  Age
#                  Institute           AZ WOMEN'S SPECI...  Ref. Physician   DR.HETAL SHAH    Sonographer        AM RDMS
#               Description       NT AMA
#         [OB]
#                    LMP(EDD) 05-11-2023                         EDD 02-15-2024                     GA(EDD) 11wéd
#                     AUA 12w4d                    EDD(AUA) 02-10-2024              Pctl. Criteria EstabDD
#                Fetal Biometry        Avg.       1        2        3                      GA                    Pctl.
#             CRL                6.07    6.06    6.07           cm         12wad+7d    Hadlock   97.72*   Rempen
#              YS               |  0.49     0.49                   cm

#                Fetal Cranium         Avg.       1        2        3                      GA                   Pctl.
#              NT               |  1.61     1.79     1.43           mm                              23.01    Yagel
#               General                                       Avq.         1          2          3
#                Fetal HR                                          155         155                               bpm

#             Comment
#             NT AMA

#              SLIUP @  12w4d (60.7MM) EDD 02/10/24 BY ULTRASOUND, SIZE C/W  DATES. YS SEEN. NT=1.4MM. NB SEEN.
#               FHR= 155BPM.
#              LT OV APPEARS WNL-SMALL FOLLICLE SEEN. RT OV NOT SEEN DUE TO GAS/BOWEL.
#              ADNEXAE APPEARS WNL.
#               POSSIBLE POST MYOMA MEASURING 3.1 X 2.7 X 2.7CM. POSSIBLE ANT SUBSEROSLAMYOMA MEASURNG 2.5 X 1.7
#                 X 2.0CM.

#              TA SCAN PERFORMED.

#            AM RDMS

#            [ Gynecology ]
#                        LMP 05-11-2023

#                 Lt. Ovary                                            Avg.          1            2           3
#                Lt Ovary L                                       3.98        3.98                               cm
#                 Lt. Ovary H                                          2.40        2.40                                 cm
#                Lt. Ovary W                                       3.68        3.68                                cm
#                  Lt. Ovary Vol.                                        18.47        18.47                                  ml
#           Images

#                             Ana                  EhaTANRE EE                                        AZ WOMENS SPECIALISTS AF 12 08-02-2023
#                             LATE  ET    i 1]      AT      aaa BA                                                 FN    aTISERIE










#                                                                                                                        08-02-2023 02:32 pm

#                                                        ULTRASOUND REPORT

#                                      AZ WOMEN'S SPECIALISTS

#                                                                                                                  WOMANS SPECALSTS MF 11 0002.2023
#                                                                                                                              LLL ERTS TET

































#                                                                                                                        08-02-2023 02:32 pm

# 
# """

#         report_text_86198 = """
#                                                   ULTRASOUND REPORT

#                                            Ultrasound Report
#  GEDme  02 GD Exam. Date 02-20-2023
#         Gender        Female              BirthDate      10-27-1994        Age             28yr 8m
#            Institute           AZ WOMEN'S SPECI ...  Diag. Physician SHAH                Ref. Physician       HETAL SHAH,...
#          Sonographer    KS.RDMS
#          Description       GROWTH
#           Al
#     [OB]
#               LMP 12-24-2022            EstabDD 09-30-2023           EDD(LMP) 09-30-2023
#          GA(LMP) 27wéd                  AUA 29w0d             EDD(AUA) 09-22-2023
#               EFW 3ib 0oz (13499)      EFW Aut... Hadlock2(BPD,...     GA(EFW) 29w2d
#         Pctl.(EFW) 71.72                Pctl. Crit... EstabDD
#          Fetal Biometry    Avg.             2       3
#                      1 1 —               aR GA Pi  it il  Pet,  1 it
#       BPD          6.98   6.98             cm     28w0d+15d  Hadl...  43.79  Hadl...
#        HC            26.62  26.62             cm      29w0d+t14d  Hadl...  56.08  Hadl...
#       AC           24.90  24.90            cm     29w1d+15d  Hadi...  79.36  Hadl...
#        FL              5.62   5.62               cm      29w4d+15d  Hadl...  81.95  Hadl...
#          General                                  Avg.       1         2         3
#         Fetal HR                            |   148      148                         bpm
#         AFI                           Last       1         2        3                          Pctl.
#        Q1                       4.77     4.77                     cm     Avg.
#       Q2                      3.41     3.41                    cm     Avg.
#       Q3                     6.08    6.08                    cm     Avg.
#       Q4                     2.72    2.72                   cm     Avg.
#         AFI                          16.98    16.98                        cm               68.38
#          Ratio           Value       |}        | 0 Normal Range  1
#         L/AC         22.57     %     (20.0~24.0%, >21w)
#        FL/BPD       80.58     %     (71.0~87.0%, >23w)
#        FL/HC         21.11      %    (17.87~21.47%, 27w...
#        HC/AC        1.07            ( 1.05~1.22, 27w6d)
#           Fetal  Description                                                       Value
#        Gender                                              Female
#          Fetal Position                                                   Breech
#         Placenta Location                                          Posterior
#         Placenta Grade                                               2
#         Amniotic Fluid                                                Normal

#       Comment





#                                                                                                                  07-07-2023 09:50 am

#                                                   ULTRASOUND REPORT

#                                             Ultrasound Report

#       GROWTH

#          Single breech female fetus with positive fetal movement.
#          FHR=154bpm with normal cardiac rhythm.
#         EFW=3#00z / 72nd%
#         AFI=17cm
#           Posterior placenta grade 2, previa seen.

#        KS.RDMS




















#                                                                                                                  07-07-2023 09:50 am

# 
# """

#         report_text_86989 = """
#                                                   ULTRASOUND REPORT

#                                            Ultrasound Report

#   4Name as               ~
#                      ID a Exam. Date    06-26-2023
#         Gender         Female              BirthDate                      Age              42yr 5m
#             Institute                                                         I
#                         AZ WOMEN'S SPECI... Diag. Physician SHAH            Ref. Physician      HETAL SHAH,...
#          Sonographer    KS.RDMS
#         Jpeseripton      ANATOMY
#                                                                                                                                              ,
#     [OB]
#               LMP 02-10-2023            EstabDD 11-17-2023           EDD(LMP) 11-17-2023
#          GA(LMP) 19w3d                  AUA 18w4d             EDD(AUA) 11-23-2023
#              EFW 0Ib100z (277g)      EFW Aut... Hadlock2(BPD,...   Pctl Crit... EstabDD
#          Fetal Biometry     Avg.     1       2       3                  G                    tl.
#                                                     :                                                               Co
#                             4.06    4.06                   cm       18w2d+12d  Hadl... "10.65 Hadl...
#       HC           15.48  15.48             cm     18w3d+10d  Hadl...  6.99  Hadl...
#       AC           13.40  13.40             cm     18w6d+14d  Hadl...  27.11  Hadi...
#        FL              3.14   3.14               cm      19wbd+13d  Hadl...  54.34  Hadl...

#         Fetal Cranium     Avg.    1      2      3                 GA               Petl.
#                        171   1.71                         .
#                                         cm     17w2d+7d ~~ Hil   5.86  Nicol...
#      CM          0.48  0.48            cm                   47.42 Nicol...
#         Lat Vent          0.55    0.55                  cm
#         General                              Avg.       1        2        3
#         Fetal HR                            |   150      150                         bpm
#         Ratio          Value                Normal Range
#        L/Ad        23.41     %     (20.0~24.0%, >21w)
#        FL/BPD       77.15     %     (71.0~87.0%, >23w)
#        FL/HC         20.25     %    (15.13~20.21%, 19w...
#        HC/AC        1.16            (1.09~1.26, 19w3d)
#        Fetal Description                                            Value
#        Gender                                               Female
#          Fetal Position                                                   Breech
#         Fetal Head                                                   Seen
#         Fetal Spine                                                     Seen
#         Placenta Location                                          Posterior
#         Placenta Grade                                              2
#         Placenta Previa                                                Yes
#        3V Cord                                            Seen
#         Cord Insertion                                                Seen
#         Amniotic Fluid                                                Normal
#          Facial Profile                                                      Not seen
#        Diaphragm                                             Seen
#         Upper Extremity                                            Seen
#         Lower Extremity                                           Seen
#        Hands                                             Seen
#         Feet                                                         Seen
#         Fetal Heart                                                     Value

#                                                                                                                   06-26-2023 02:02 pm

#                                                   ULTRASOUND REPORT

#                                            Ultrasound Report

#         Fetal Heart                                               ,,Value
#        4 Chamber                                          Not seen
#          Lt. Outflow Tract                                             Not seen
#          Rt. Outflow Tract                                            Not seen
#          3 Vessel                                                    Not seen
#          Aortic Arch                                                 Not seen
#          Ductal Arch                                                Not seen
#         Cardiac Rhythm                                         Not seen
#          Fetal Brain                                                      Value
#          Lateral Ventricles                                                Seen
#         Cerebellum                                               Seen
#         Cist Magna                                                Seen
#        Cranium                                              Seen
#         Fetal Abdomen                                            Value
#         Abdominal Wall                                            Seen
#         Spine                                                    Seen
#        Stomach                                            Seen
#         Bladder                                                   Seen
#          Lt. Kidney                                                     Seen
#          Rt. Kidney                                                     Seen
#        Maternal Others                       Avg.       1        2
#         Cervix L                             |   7.34      7.34                          cm

#       Comment
#       ANATOMY

#          Single female fetus seen with positive fetal movement.
#         FHR=150bpm with normal cardiac rhythm.
#        EFW=100z
#          Amniotic fluid appears wnl.
#          Anatomy well visualized with the exception of limited facial and cardiac views due to
#          persistent fetal lie, no obvious abnormalities seen.
#          Posterior placenta grade 2, complete previa seen.
#         The cervix was seen transabdominally measuring 7.3cm

#        KS.RDMS






#                                                                                                                  06-26-2023 02:02 pm

# 
# """
        
#         report_text_87534 = """
#                                                       ULTRASOUND REPORT

#                                      AZ WOMEN'S SPECIALISTS

#             Name                           ID                         Exam. Date       08-03-2023
#              Gender         Female              BirthDate                       Age              29yr 8m
#                  Institute           AZ WOMEN'S SPECI...  Ref. Physician                HAH    Sonographer        KS.RDMS
#               Description       GROWTH
#         [OB]
#                   LMP(EDD) 01-17-2023                         EDD 10-24-2023                     GA(EDD) 28w2d
#                     AUA 30w1d                    EDD(AUA) 10-11-2023                     EFW 3ib 50z (1510g)
#                EFW Author Hadlock4(BPD,HC,A...       Pctl.(EFW) 93.42"                    Pctl. Criteria EstabDD

#                Fetal Biometry         Avg.       1        2        3                      GA                    Pctl.
#            BPD              7.39    7.39                cm        29w4d+15d ~~ Hadlock   79.69   Hadlock
#              HC                 27.94    27.94                  cm        30wddt21d    Hadlock   85.47   Hadlock
#             AC                25.57    25.57                 cm        29w5d+15d   Hadlock  83.72   Hadlock
#                 FL                     5.86      5.86                       cm   Last    30w4d+21d    Hadlock    91.46    Hadlock
#               General                                       Avg.         1          2          3
#                Fetal HR                                      |    154         154                               bpm
#                 AFI                                    Avg.          1           2           3                                 Pctl.
#               Q1                                  8.43       8.43                             cm
#              Q2                              7.19       7.19                           cm
#              Q3                              2.71       2.71                           cm
#          Q4                       6.93     6.93                    cm
#             AFI                            25.26      25.26                         cm                98.28*
#             Ratio             Value                    Normal Range
#                  FL/IAC                22.91          %            (20.0~24.0%, >21w)
#              FL/BPD            79.32       %         (71.0~87.0%, >23w)
#               FL/HC              20.97        %        (18.21~21.47%, 28w2d)
#              HC/AC             1.09                  (1.03~1.22, 28w2d)
#                Fetal Description                                                             Value
#              Gender                                                          Male
#                 Fetal Position                                                                   Vertex
#                Placenta Location                                                        Anterior
#               Placenta Grade                                                            2
#                Amniotic Fluid                                                             Normal

#            Comment
#            GROWTH

#                 Single vertex male fetus seen with + fetal movement.
#                FHR=154bpm with normal cardiac rhythm.
#               EFW=3#50z / 93rd%
#                 Anterior placenta grade 2.
#                AFI1=25.3cm / polyhydramnios

#             KS.RDMS









#                                                                                                                         08-03-2023 11:02 am

# """
        
#         report_text_88359 = """
#                                                   ULTRASOUND REPORT

#                                             Ultrasound Report

#         Name                           ID                         Exam. Date       08-04-2023
#          Gender        Female                                            Age              24yr 8m
#                                                .
#             Institute           AZ WOMEN'S SPECI.    Diag. Physician SHAH                Ref. Physician       HETAL SHAH,...
#          Sonographer    KS.RDMS
#           Description       ANATOMY
#            .
#     [OB]
#         LMP(EDD) 03-05-2023            EstabDD 12-10-2023                EDD 12-10-2023
#          GA(EDD) 21w5d                  AUA 22w1d             EDD(AUA) 12-07-2023
#               EFW 1ib 30z (531g)       EFW Aut... Hadlock2(BPD,...    GA(EFW) 22w2d
#          Pctl. Crit... EstabDD
#          Fetal Biometry    Avg.     1       2       3                  GA                Pctl.
#       BPD          5.27   5.27             cm     22w0d+12d  Hadl   59.81  Hadl...
#       HC           19.87  19.87            cm     22w0d+10d  Hadl   53.40  Hadl...
#       AC           18.43  18.43            cm     23w2d+14d  Hadl   86.41  Hadl...
#        FL             3.83   3.83               cm      22w2d+13d  Hadl    59.29  Hadl...

#         Fetal Cranium     Avg. 1     2      3
#                                                                                              |  |   GA |          ERI       Petl,    Ig    !
#       CEREB        225   2.25             cm     21w1d+13d   Hill   60.90 Nicol...
#       CM          0.53  0.53            cm                   46.70 Nicol...
#            Vent         0.64   0.64                cm
#            | Lat
#         General
#                                                                     Ave '         A,            2            3
#         Fetal HR                                1         140                         bpm
#          Ratio           Value               yNormal Range
#       FLAC       20.78    %     (20.0~24.0%, >21w)
#        FL/BPD       72.63     %     (71.0~87.0%, >23w)
#        FL/HC         19.27     %    (16.41~21.50%, 21w...
#        HC/AC        1.08            (1.06~1.25, 21w5d)
#         Fetal Description                                             Value
#        Gender                                              Male
#          Fetal Position                                                   Breech
#         Fetal Head                                                   Seen
#          Fetal Spine                                                     Seen
#         Placenta Location                                           Anterior
#         Placenta Grade                                               2
#          Placenta Previa                                                Yes
#        3V Cord                                            Seen
#          Cord Insertion                                                 Seen
#          Amniotic Fluid                                                Normal
#           Facial Profile                                                        Seen
#        Diaphragm                                            Seen
#         Upper Extremity                                            Seen
#         Lower Extremity                                            Seen
#        Hands                                              Seen
#         Feet                                                       Seen

#                                                                                                                    08-04-2023 03:24 pm

#                                                   ULTRASOUND REPORT

#                                             Ultrasound Report

#         Fetal Heart                         -                       Value
#        4 Chamber                                            Seen
#          Lt. Outflow Tract                                               Seen
#          Rt. Outflow Tract                                              Seen
#          3 Vessel                                                      Seen
#          Aortic Arch                                                   Seen
#          Ductal Arch                                                  Seen
#         Cardiac Rhythm                                         Regular
#          Fetal Brain                                                       Value
#          Lateral Ventricles                                                Seen
#         Cerebellum                                                 Seen
#         Cist Magna                                                Seen
#        Cranium                                              Seen
#         Fetal Abdomen                                           Value
#         Abdominal Wall                                            Seen
#         Spine                                                    Seen
#        Stomach                                            Seen
#         Bladder                                                    Seen
#          Lt. Kidney                                                      Seen
#          Rt. Kidney                                                    Seen

#         Maternal Others                        Avg.       1         2        3
#          Cervix L                              |   s.09      6.09                          cm

#        Comment
#       ANATOMY

#          Single male fetus seen with positive fetal movement.
#         FHR=140bpm with normal cardiac rhythm.
#        EFW=1#30z
#          Amniotic fluid appears wnl.
#          Anatomy well visualized, no obvious abnormalities seen with the exception of an EIF seen
#          in the left ventricle. Suboptimal views of nasal bone and cisterna magna.
#           Anterior placenta grade 2, partial previa seen. Covering the 10S by 1.5cm.
#          The cervix was seen transabdominally measuring 6.1cm.

#        KS.RDMS






#                                                                                                                   08-04-2023 03:24 pm

# 
# """
        
        json_data = text_to_json(report_text_85978)
        # final_response = parse_report(json_data)

        print(json_data)
        # print("---------------------------")
        json_data_pure = remove_null_keys(json_data)
        print(json_data_pure)
        print("cleaned data................")
        # return jsonify({"message": "File uploaded successfully."}), 200
        # return jsonify({"response": final_response})
        data = {'query': str(json_data_pure), type: ''}
        return ultrabot.get_response(data)
    else:
        return jsonify({"message": "No file uploaded."}), 400

if __name__ == '__main__':
    IP = ip_config[environment]
    response_port = config['BotApplication']['Backend']  # response API
    app.run(host='0.0.0.0', port=response_port)

