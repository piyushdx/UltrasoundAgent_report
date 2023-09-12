
insightsAll = {
    "Fetal HR avg value": {
      "normal_values": "For Fetal HR 120 to 160 bpm is normal range",
      "abnormal_values": "For Fetal HR <120 bpm and >160 bpm is abnormal range",
      "check": "yes"
    },
    "AFI cm value": {
      "normal_values": "For AFI 5 to 25 cm value is considered as normal",
      "abnormal_values": "For AFI  <5 cm and >25 cm value is considered as abnormal",
      "check": "yes"
    },
    "AFI pctl value": {
      "normal_values": "For AFI 5th to 95th percentile is considered as normal",
      "abnormal_values": "For AFI <5th percentile and >95th percentile is considered as abnormal",
      "check": "yes"
    },
    "Gender": {
      "normal_values": "Male and Female is normal values of gender",
      "abnormal_values": "Others are abnormal value",
      "check": "yes"
    },
    "Fetal Position": {
      "normal_values": "Normal Fetal positions are Head down (vertex), Anterior and Posterior",
      "abnormal_values": "Abnormal Fetal positions are  Transverse, Shoulder Presentation and Head up (breech)",
      "check": "yes"
    },
    "Placenta Location": {
      "normal_values": "Normal placenta location are Anterior, Posterior, Fundal",
      "abnormal_values": "Abnormal placenta location are Placenta Previa,vasa previa,Accreta,Percreta,Marginal and Low-lying, ",
      "check": "yes"
    },
    "Placenta Grade": {
      "normal_values": "Placenta Grade <=2 is considered as normal",
      "abnormal_values": "Placenta Grade 3 or more considered as abnormal",
      "check": "yes"
    },
    "Amniotic Fluid": {
      "normal_values": "Value of Amniotic Fluid Adequate or Normal is fine.",
      "abnormal_values": "Abnormal values fo Amniotic Fluid are Low, High, Oligohydramnios and Polyhydramnios",
      "check": "yes"
    },
    "Fetal Movements": {
      "normal_values": "Normal values of Fetal Movements are Regular, frequent Or 2",
      "abnormal_values": "Abnormal values of Fetal Movements are Decreased, Absent, Hyperactive Or <=1",
      "check": "yes"
    },
    "Fetal Tone": {
      "normal_values": "Normal Values of Fetal Tones is Normal Or 2",
      "abnormal_values": "Abnormal values of Fetal Tones are Hypotonia Hypertonia Or <=1",
      "check": "yes"
    },
    "Fetal Breathing Move": {
      "normal_values": "Normal Values of Fetal Breathing Move are Present Or 2",
      "abnormal_values": "Abnormal Values of Fetal Breathing Move are Absent Or <=1",
      "check": "yes"
    },
    "Amniotic Fluid Volume": {
      "normal_values": "Normal values of Amniotic Fluid volume are Normal,Adequate Or 2",
      "abnormal_values": "Abnormal values of Amniotic Fluid volume are Low, High, Oligohydramnios, Polyhydramnios Or <=1",
      "check": "yes"
    },
    "Total out of 8": {
      "normal_values": "Normal Value of Total out of 8 is 8",
      "abnormal_values": "Abnormal value of Total out of 8 is <8",
      "check": "yes"
    },
    "AC value in pctl": {
      "normal_values": "Normal Value of AC are >10th ptcl to <90th ptcl",
      "abnormal_values": "Abnormal value of AC are <10th ptcl and >90th ptcl",
      "check": "yes"
    }
  }

reportString = """{
  "LMP(EDD)": "10-08-2022",
  "LMP": "10-08-2022",
  "EstabDD": "07-15-2023",
  "EDD": "07-15-2023",
  "GA(EDD)": "39w4d",
  "Fetal HR avg value": "142",
  "AFI cm value": "17.13",
  "AFI pctl value": "79.14",
  "Gender": "Female",
  "Fetal Position": "Shoulder presentation",
  "Placenta Location": "Low-lying",
  "Placenta Grade": "2",
  "Amniotic Fluid": "Normal",
  "Fetal Movements": "2",
  "Fetal Tone": "2",
  "Fetal Breathing Move": "2",
  "Amniotic Fluid Volume": "2",
  "Total out of 8": "8",
  "AC value in cm": "8.2",
}"""

# import json

# report = json.loads(reportString)
# if "10-08-2022" in report.values():
#     print("yes")

# normal_keys = []
# for k, v in report.items():
#     if v == 'Normal':
#         normal_keys.append(k)

# print(normal_keys)
