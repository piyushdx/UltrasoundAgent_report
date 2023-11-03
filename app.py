import chromadb
import json
import openai
from create_pdf_list import ele1, ele2, ele3, ele4, ele5, ele6, ele7, ele8, ele9, ele10, ele11, ele12, ele13, ele14, ele15, ele16, ele17, ele18, ele19, ele20, ele21, ele22, ele23, ele24, ele25, ele26, ele27, ele28, ele29, ele30, ele31, ele32, ele33, ele34, ele35, ele36, ele37, ele38, ele39, ele40, ele41, ele42, ele43, ele44, ele45, ele46, ele47, ele48, ele49, ele50, ele51, ele52, ele53, ele54, ele55, ele56, ele57, ele58, ele59, ele60, ele61, ele62, ele63, ele64, ele65, ele66, ele67, ele68, ele69, ele70, ele71, ele72, ele73, ele74, ele75, ele76, ele77, ele78, ele79, ele80, ele81, ele82, ele83, ele84

class VectorDB():
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("ultrasound_data")
        self.collection.add(
                    documents=[str(ele1), str(ele2), str(ele3), str(ele4), str(ele5), str(ele6), str(ele7), str(ele8), str(ele9), str(ele10), str(ele11), str(ele12), str(ele13), str(ele14), str(ele15), str(ele16), str(ele17), str(ele18), str(ele19), str(ele20), str(ele21), str(ele22), str(ele23), str(ele24), str(ele25), str(ele26), str(ele27), str(ele28), str(ele29), str(ele30), str(ele31), str(ele32), str(ele33), str(ele34), str(ele35), str(ele36), str(ele37), str(ele38), str(ele39), str(ele40), str(ele41), str(ele42), str(ele43), str(ele44), str(ele45), str(ele46), str(ele47), str(ele48), str(ele49), str(ele50), str(ele51), str(ele52), str(ele53), str(ele54), str(ele55), str(ele56), str(ele57), str(ele58), str(ele59), str(ele60), str(ele61), str(ele62), str(ele63), str(ele64), str(ele65), str(ele66), str(ele67), str(ele68), str(ele69), str(ele70), str(ele71), str(ele72), str(ele73), str(ele74), str(ele75), str(ele76), str(ele77), str(ele78), str(ele79), str(ele80), str(ele81), str(ele82), str(ele83), str(ele84)], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
                    metadatas=[{"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}], # filter on these!
                    ids=["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q27", "q28", "q29", "q30", "q31", "q32", "q33", "q34", "q35", "q36", "q37", "q38", "q39", "q40", "q41", "q42", "q43", "q44", "q45", "q46", "q47", "q48", "q49", "q50", "q51", "q52", "q53", "q54", "q55", "q56", "q57", "q58", "q59", "q60", "q61", "q62", "q63", "q64", "q65", "q66", "q67", "q68", "q69", "q70", "q71", "q72", "q73", "q74", "q75", "q76", "q77", "q78", "q79", "q80", "q81", "q82", "q83", "q84"], # unique for each doc
                )

    def get_context(self,que):
        results = self.collection.query(
                    query_texts=[que],
                    n_results=2,
                )
        return results

    def get_context_combined(self,results):
        context = ""
        page_number = set()
        for ele in results['documents'][0]:
            print(ele)
            page_number.add(json.loads(ele.replace("\'","\""))['page'])
            chunk = json.loads(ele.replace("\'","\""))
            final_ans = chunk['title'] + "::\n"
            for key, value in chunk['content'].items():
                f,s = key.split(" ")
                if s == "extra":
                    final_ans += value + "\n"
                elif s == "G":
                    final_ans += value + "\n"
                else:
                    pass
            context += final_ans + "\n\n"
        return context,page_number

# question = "I would like comprehensive guidelines for Socio-Demographic Risk Factors (maternal age) Age ≥ 35 along with CPT reports.if there is any.\n"
# question = "I would like comprehensive guidelines for placenta previa along with CPT reports.if there is any.\n"
# db = VectorDB()
# results = db.get_context(question)
# context,page = db.get_context_combined(results)
# print(context)
# print(page)

# prompt_template = f""" Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.
# [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
#     1.Answer questions based solely on provided context. do not infer or generate your own answers.
#     2.if no relevant answer found at all then say and only say "No specific CPT reports are mentioned in the context"
#     3.If the key analysis suggests that the condition is considered normal, commonly encountered,common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"

# [Sample Question]
#     I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
# [Sample Output] 
#     Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
#         actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
#         Circumference ≤10th percentile.
#     Recommendation:
#         • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
#         • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
#         can be performed once or twice weekly
#         • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
#         weekly
#         • Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
#         performed every 2 to 4 weeks if complete anatomy ultrasound previously performed

# Context : <context>
# """

# def get_completion(prompt, model="gpt-3.5-turbo"):
#     # messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=prompt,
#         temperature=0.4  # this is the degree of randomness of the model's output
#     )
#     return response.choices[0].message["content"]

# db = VectorDB()

# I would like comprehensive guidelines for the Socio-Demographic Risk Factors (maternal age) Age ≥ 35 along with CPT reports.if there is any.
# I would like comprehensive guidelines for the placenta previa along with CPT reports.if there is any.

# while True:
#     question = str(input("Query : "))
#     results = db.get_context(que=question)
#     context = get_context_combined(results)
#     history = [{"role": "system", "content": prompt_template.replace("<context>",context)},{"role": "user", "content": f"{question}" }]
#     print("below is the history\n\n")
#     print(history)
#     output = get_completion(history)
#     print("\n\n")
#     print(output)
#     print("\n\n")


# def get_completion(prompt, model="gpt-3.5-turbo"):
#     # messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=prompt,
#         temperature=0.4  # this is the degree of randomness of the model's output
#     )
#     return response.choices[0].message["content"]

# history = [{'role': 'system', 'content': ' Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.\n[STRICT RULES TO FOLLOW WHILE GIVING ANSWER]\n    1.Answer questions based solely on provided context. do not infer or generate your own answers.\n    2.if no relevant answer found at all then say and only say "No specific CPT reports are mentioned in the context"\n    3.If the key analysis suggests that the condition is considered normal, commonly encountered,common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"\n\n[Sample Question]\n    I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"\n[Sample Output] \n    Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or\n        actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal\n        Circumference ≤10th percentile.\n    Recommendation:\n        • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed\n        • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)\n        can be performed once or twice weekly\n        • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed\n        weekly\n        • Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be\n        performed every 2 to 4 weeks if complete anatomy ultrasound previously performed\n\nContext : Previa (Placenta Previa and Vasa Previa)::\nSecond and Third Trimesters:For known placenta previa (placental edge covers the internal cervical os) or low lying placenta (placental edge <2 cm from internal os):One routine follow-up ultrasound can be performed in the 3rd trimester (CPT® 76815 or CPT® 76816 and/or CPT® 76817).If placenta previa or low lying placenta is still present, one follow-up ultrasound (CPT® 76815 or CPT® 76816 and/or CPT® 76817) can be performed in 3-4 weeks.If persistent placenta previa (placental edge covers the internal cervical os), BPP (CPT® 76818/CPT® 76819 or modified BPP (CPT® 76815) weekly, starting at 32 weeks.Follow-up ultrasound can be performed at any time if bleeding occurs BPP (CPT® 76818 or CPT® 76819) or CPT® 76815 or CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817).Background and Supporting Information:For pregnancies beyond 16 weeks, if the placental edge is ≥2 cm away from the internal os, the placental location should be reported as normal.If the placental edge is <2 cm from the internal os but not covering the internal os, it should be labeled as low lying.If the placental edge covers the internal cervical os, the placenta should be labeled as a placenta previa.There is no evidence to guide the optimal time of subsequent imaging in pregnancies thought to have placenta previa. In stable patients it is reasonable to perform a follow-up ultrasonogram at approximately 32 weeks of gestation and an additional study at 36 weeks of gestation (if the previa persists) to determine the optimal route and timing of delivery. There is no clear benefit from more frequent ultrasonograms (eg, every 4 weeks) in stable cases.\nVasa Previa:Vasa previa occurs when fetal blood vessels that are unprotected by the umbilical cord or placenta run through the amniotic membranes and cross over the internal cervical os.If a Vasa Previa is found on initial imaging:\nDetailed anatomic ultrasound at ≥16 weeks:The fetal anatomy survey (CPT® 76805/CPT® 76811) is optimally performed at 18 to 22 weeks of gestation, though it can be conducted as early as 14 weeks gestation, per ACOG guidelines.\nFollow-up growth ultrasound every 2 to 4 weeks starting at ≥23 weeks:CPT® 76816 and/or19 CPT® 76817\nOnce vasa previa is confirmed cervical length screening every 2 to 4 weeks starting at 28 weeks:CPT® 76817 and CPT® 76816 or CPT® 76815.\nBPP or modified BPP weekly starting at 32 weeks (can be performed earlier and/or more frequently if worsening fetal condition suspected):CPT® 76818 or CPT® 76819 (BPP) or CPT® 76815\n\n\nRequired Elements for Complete First Trimester Ultrasound::\n• Complete First Trimester Ultrasound (CPT® 76801 and CPT® 76802) should only be reported once per pregnancy/per practice/facility unless the mother changes to a new medical caregiver at a new practice/facility and there is a new medical indication for ultrasound.\n\n\n\n'}, {'role': 'user', 'content': 'I would like comprehensive guidelines for the placenta previa along with CPT reports.if there is any.'}]
# output = get_completion(history)
# print(output)
# history = [{'role': 'system', 'content': ' Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.\n[STRICT RULES TO FOLLOW WHILE GIVING ANSWER]\n    1.Answer questions based solely on provided context. do not infer or generate your own answers.\n    2.if no relevant answer found at all then say and only say "No specific CPT reports are mentioned in the context"\n    3.If the key analysis suggests that the condition is considered normal, commonly encountered,common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"\n\n[Sample Question]\n    I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"\n[Sample Output] \n    Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or\n        actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal\n        Circumference ≤10th percentile.\n    Recommendation:\n        • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed\n        • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)\n        can be performed once or twice weekly\n        • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed\n        weekly\n        • Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be\n        performed every 2 to 4 weeks if complete anatomy ultrasound previously performed\n\nContext : High Risk Group One - Risk Factors | Socio-Demographic Risk Factors (maternal age)::\nAge ≥35 years of age at the estimated date of confinement (EDC)\nDetailed Fetal Anatomic Scan CPT® 76811 if ≥16 weeks: \nThough CPT® 76811 can be performed as early as 14 weeks gestation, per ACOG, in the absence of other specific indications, it is optimally performed at 18 to 22 weeks of gestation.\nStarting at 23 weeks, follow-up growth scans (CPT® 76816) every 3 to 6 weeks.\nBPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815), weekly starting at 32 weeks.\nStarting at 32 weeks, perform BPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815) up to 2x weekly for the following conditions: - Antiphospholipid Syndrome. - Maternal Renal Disease (moderate to severe with creatinine >1.4mg/dl). - Sickle cell disease.\nStarting at diagnosis, perform BPP (CPT® 76818 or CPT® 76819) if ≥26 weeks, or modified BPP (CPT® 76815) if ≥23 weeks, up to 2x weekly for the following conditions: - Intra-hepatic cholestasis of pregnancy (IHCP). - Complicated Sickle cell disease (e.g. co-existing hypertension, vaso-occlusive crisis, fetal growth restriction). - Complicated SLE (e.g. active lupus nephritis, or recent flares). - Major fetal anomaly in the current pregnancy (e.g. gastroschisis, fetal ventriculomegaly, fetal hydronephrosis (>10mm), achondroplasias, fetal congenital heart disease, neural tube defect, sustained fetal arrhythmias).\n\n\nHypertensive Disorders in Pregnancy::\nScreening in High Risk Groups\nSMFM state that uterine artery Doppler has limited diagnostic accuracy and clinical utility in predicting FGR, SGA birth, and perinatal mortality. As such, its use for screening in high risk groups is not recommended.\n\nCurrent Chronic Hypertension Not on Medication (OB-9.8.2)\nFetal anatomic scan CPT® 76811 Once after 16 weeks\nUltrasound (for fetal growth) In the third trimester (≥28 weeks) Every 4-6 weeks CPT® 76816\nif blood pressure is elevated from baseline, See Gestational Hypertension (GH, preeclampsia, toxemia) (OB-9.8.4)\n\nCurrent Chronic Hypertension on Medication (OB-9.8.3)\nUltrasound (for fetal growth) Starting at viability 23 weeks gestation Every 3 to 4 weeksCPT® 76816\nBiophysical profile (BPP) or modified BPP Starting at 32 weeks If complicated by other risk factors (e.g. DM, FGR Oligohydramnios) can start at ≥26 weeks) Once weekly If complicated by other risk factors (e.g., FGR Oligohydramnios) twice weekly CPT® 76818 (BPP) or CPT® 76819 (BPP) or CPT® 76815 (AFI)\n\nGestational Hypertension (GH, Preeclampsia, Toxemia)\nGrowth US Starting at time of diagnosis Every 3 to 4 weeks If FGR, Oligohydramnio s or severe preeclampsia (every 2 to 4 weeks) CPT® 76816\nBPPStarting at time of diagnosis if ≥26 weeks Up to twice weekly Hypertension/ pre-eclampsia with severe features - Daily then do CPT® 76818 or CPT® 76819\nBackground and Supporting Information\n Hypertension in pregnancy - Systolic blood pressure ≥140 mm Hg or diastolic BP ≥90 mm Hg, or both, measured on two occasions at least 4 hours apart\n Severe-range hypertensionSystolic blood pressure ≥160 mm Hg or diastolic BP ≥110 mm Hg, or both, measured on two occasions at least 4 hours apart\n Chronic hypertensionHypertension diagnosed or present before pregnancy or before 20 weeks of gestation; or hypertension that is diagnosed for the first time during pregnancy and that does not resolve in the postpartum period\n Chronic hypertension with superimposed preeclampsiaPreeclampsia in a woman with a history of hypertension before pregnancy or before 20 weeks of gestation\n Gestational hypertensionHypertension diagnosed after 20 weeks of gestation, in a woman with a previously normal blood pressure.\n PreeclampsiaDisorder of pregnancy associated with new-onset hypertension, which occurs most often after 20 weeks of gestation and frequently near term. Although often accompanied by new-onset proteinuria, hypertension and other signs or symptoms of preeclampsia may present in some women in the absence of proteinuria.\n Eclampsia Convulsive manifestation of the hypertensive disorders of pregnancy and is among the more severe manifestations of the disease.\n\n\n\n'}, {'role': 'user', 'content': 'I would like comprehensive guidelines for the Socio-Demographic Risk Factors (maternal age) Age ≥ 35 along with CPT reports.if there is any.'}]
# history = [{'role': 'system', 'content': ' Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.\n[STRICT RULES TO FOLLOW WHILE GIVING ANSWER]\n    1.Answer questions based solely on provided context. do not infer or generate your own answers.\n    2.if no relevant answer found at all then say and only say "No specific CPT reports are mentioned in the context"\n    3.If the key analysis suggests that the condition is considered normal, commonly encountered,common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"\n\n[Sample Question]\n    I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"\n[Sample Output] \n    Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or\n        actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal\n        Circumference ≤10th percentile.\n    Recommendation:\n        • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed\n        • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)\n        can be performed once or twice weekly\n        • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed\n        weekly\n        • Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be\n        performed every 2 to 4 weeks if complete anatomy ultrasound previously performed\n\nContext : Abnormal Fetal Position/Presentation::\nTo confirm suspected abnormal fetal position or presentation (transverse or breech presentation) at ≥36 weeks gestation, report one of the following:• CPT® 76805 (plus CPT® 76810 for each additional fetus) when a complete anatomy scan has not yet been performed in the pregnancy or\n• CPT® 76815 for a limited ultrasound to check fetal position or\n• CPT® 76816 if version is being considered and/or for delivery planning.\nBackground and Supporting Information:Fetal presentation should be assessed by abdominal palpation (Leopold’s) at 36 weeks or later, when presentation is likely to influence the plans for the birth. Routine assessment of presentation by abdominal palpation before 36 weeks is not always accurate. Suspected fetal malpresentation should be confirmed by an ultrasound assessment. An ultrasound can be performed at ≥36 weeks gestation to determine fetal position to allow for external cephalic version. Ultrasound to determine fetal position is not necessary prior to 36 weeks gestation unless delivery is imminent.\n• CPT® 76815 should never be reported with complete studies CPT® 76801/CPT® 76802, CPT® 76805/CPT® 76810 or CPT® 76811/CPT® 76812 or with CPT® 76816 or BPP (CPT® 76818 and CPT® 76819).\n\n\nFetal Anatomic Scan::\nThough fetal anatomy survey (CPT 76805/CPT 76811) can be performed as early as 14 weeks gestation, per ACOG, in the absence of other specific indications, it is optimally performed at 18 to 22 weeks of gestation. This timing allows for a survey of fetal anatomy and an accurate estimation of gestational age.\nFor a normal/low risk pregnancy, report a fetal anatomy ultrasound CPT® 76805 if ≥16 weeks.\nIf high risk indication is met can report:\nThese high risk scans indication driven and generally performed by a Maternal Fetal Medicine (MFM) specialist/Perinatologist, or a Radiologist at an AIUM or ACR accredited facility.\n\n\n\n'}, {'role': 'user', 'content': 'I would like comprehensive guidelines for the fetal position breech along with CPT reports.if there is any.'}]


# import pickle

# db = VectorDB()
# result = db.get_context("hello")
# with open('db.pkl', 'wb') as f:
#     pickle.dump(result, f)

# with open('db.pkl', 'rb') as f:
#     db = pickle.load(f)

# results = db.query(
#             query_texts=["placenta previa"],
#             n_results=2,
#         )
# print(results)

# client = chromadb.Client()
# collection = client.create_collection("ultrasound_data")
# collection.add(
#             documents=[str(ele1), str(ele2), str(ele3), str(ele4), str(ele5), str(ele6), str(ele7), str(ele8), str(ele9), str(ele10), str(ele11), str(ele12), str(ele13), str(ele14), str(ele15), str(ele16), str(ele17), str(ele18), str(ele19), str(ele20), str(ele21), str(ele22), str(ele23), str(ele24), str(ele25), str(ele26), str(ele27), str(ele28), str(ele29), str(ele30), str(ele31), str(ele32), str(ele33), str(ele34), str(ele35), str(ele36), str(ele37), str(ele38), str(ele39), str(ele40), str(ele41), str(ele42), str(ele43), str(ele44), str(ele45), str(ele46), str(ele47), str(ele48), str(ele49), str(ele50), str(ele51), str(ele52), str(ele53), str(ele54), str(ele55), str(ele56), str(ele57), str(ele58), str(ele59), str(ele60), str(ele61), str(ele62), str(ele63), str(ele64), str(ele65), str(ele66), str(ele67), str(ele68), str(ele69), str(ele70), str(ele71), str(ele72), str(ele73), str(ele74), str(ele75), str(ele76), str(ele77), str(ele78), str(ele79), str(ele80), str(ele81), str(ele82), str(ele83), str(ele84)], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
#             metadatas=[{"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}], # filter on these!
#             ids=["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q27", "q28", "q29", "q30", "q31", "q32", "q33", "q34", "q35", "q36", "q37", "q38", "q39", "q40", "q41", "q42", "q43", "q44", "q45", "q46", "q47", "q48", "q49", "q50", "q51", "q52", "q53", "q54", "q55", "q56", "q57", "q58", "q59", "q60", "q61", "q62", "q63", "q64", "q65", "q66", "q67", "q68", "q69", "q70", "q71", "q72", "q73", "q74", "q75", "q76", "q77", "q78", "q79", "q80", "q81", "q82", "q83", "q84"], # unique for each doc
#         )

# results = collection.query(
#             query_texts=["placenta previa"],
#             n_results=2,)

# print(results)

#--------------------92295
# ALEX
# 19:50
# Fetal Position : Transverse

# Key Analysis: Suspected abnormal fetal position/transverse presentation at ≥36 weeks gestation.
# Recommendation:
# - If a complete anatomy scan has not yet been performed in the pregnancy, report CPT® 76805 (plus CPT® 76810 for each additional fetus).
# - If fetal position needs to be checked, report CPT® 76815 for a limited ultrasound.
# - If version is being considered and/or for delivery planning, report CPT® 76816.
# - Do not report CPT® 76815 with complete studies CPT® 76801/CPT® 76802, CPT® 76805/CPT® 76810, CPT® 76811/CPT® 76812, or with CPT® 76816 or BPP (CPT® 76818 and CPT® 76819).

# ALEX
# 19:50
# Suboptimal spine and kidneys :

# Key Analysis: Suboptimal spine and kidneys.

# Recommendation:
# - A detailed fetal anatomic evaluation ultrasound (CPT® 76811) should be performed to assess the suboptimal spine and kidneys.
# - The detailed fetal anatomy scan (CPT® 76811) includes a comprehensive evaluation of the head, face, neck, chest/heart, abdomen, spine, extremities, genitalia, placenta, fetal number and presentation, qualitative or semi-qualitative estimate of amniotic fluid, maternal anatomy, and fetal biometry.
# - Follow-up studies to the detailed fetal anatomy scan (CPT® 76811) should be coded as CPT® 76815 or CPT® 76816.

# No specific CPT reports are mentioned in the context.
# ALEX
# 19:50
# Limited scan due to MBH :

# Key Analysis: Limited scan due to MBH (Marginal Cord Insertion) is a condition where the umbilical cord is attached to the edge of the placenta instead of the center. It can be associated with certain risks and complications.
# Recommendation:
# - Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed.
# - Follow-up ultrasound (CPT® 76816) can be performed every 2 to 4 weeks if complete anatomy ultrasound previously performed.
# - Umbilical artery (UA) Doppler (CPT® 76820) can be performed to assess blood flow to the fetus.
# - Growth scans can be considered to monitor fetal growth and well-being.
# No specific CPT reports are mentioned in the context.