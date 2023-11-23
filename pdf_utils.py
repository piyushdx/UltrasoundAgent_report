from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
load_dotenv()
import openai
import re
import json

def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def find_and_extract_abnormalities(text):
    words = text.split()
    occurrences = []

    for i in range(len(words)):
        if words[i] == 'suspected' or words[i] == 'known':
            # Ensure there are at least two words following "suspected" or "known"
            if i + 3 <= len(words):
                context = ' '.join(words[i:i+3])
                occurrences.append(context)
    return occurrences

def find_changes_in_first_word(text_list):
    # Initialize a dictionary to store the unique text after the first word
    unique_texts = {}
    changes = []
    final_list = []

    # Iterate through the list
    for text in text_list:
        # Split the text into words
        words = text.split()

        # Check if there is at least one word after the first word
        if len(words) > 1:
            # Extract the first word and the rest of the text
            first_word = words[0]
            rest_of_text = ' '.join(words[1])

        if rest_of_text not in final_list:
            final_list.append(rest_of_text)
        else:
            changes.append(" ".join(words[1:]))
            # # Check if the rest of the text is already associated with a different first word
            # if rest_of_text in unique_texts:
            #     # If it is, check if the first words differ
            #     if unique_texts[rest_of_text] != first_word:
            #         changes.append(rest_of_text)
            # else:
            #     # If it's not, store the first word as the key and the rest of the text as the value
            #     unique_texts[rest_of_text] = first_word
    
    return changes

ans_for_age = """
Key Analysis: 
Maternal age ≥ 35 is considered a socio-demographic risk factor. Advanced maternal age is associated with an increased risk of various complications during pregnancy, such as gestational diabetes, preeclampsia, and chromosomal abnormalities in the fetus.

Recommendation: 
- Complete first trimester ultrasound CPT® 76801 [plus CPT® 76802 for each additional fetus] if <14 weeks and a complete ultrasound has not yet been performed, and/or CPT® 76817 for a transvaginal ultrasound
    - CPT® 76801 is preferred for dating, but if this is unable to be completed then
    - CPT® 76815 and/or CPT® 76817 for a transvaginal ultrasound is indicated
    - See Detailed First Trimester Fetal Anatomic Scan (OB-9.12) for indications for detailed first trimester fetal anatomic evaluation 5,6
- Detailed Fetal Anatomic Scan CPT® 76811 if ≥16 weeks
    - Though CPT® 76811 can be performed as early as 14 weeks gestation, per ACOG, in the absence of other specific indications, it is optimally performed at 18 to 22 weeks of gestation
- Starting at 23 follow-up growth scans (CPT® 76816) every 3 to 6 weeks
- BPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815), weekly starting at 32 weeks
- More frequent antepartum fetal surveillance can be performed as stipulated below:
	- Starting at 32 weeks, perform BPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815) up to 2x weekly for the conditions below:
	- Antiphospholipid Syndrome
	- Maternal Renal Disease (moderate to severe with creatinine >1.4mg/dl)
	- Sickle cell disease
- Starting at diagnosis perform BPP (CPT® 76818 or CPT® 76819) if ≥26 weeks, or modified BPP (CPT® 76815) if ≥23 weeks, up to 2x weekly:
	- Intra-hepatic cholestasis of pregnancy (IHCP)
	- Complicated Sickle cell disease (e.g. co-existing hypertension, vaso-occlusive crisis, fetal growth restriction)
	- Complicated SLE (e.g. active lupus nephritis, or recent flares)
	- Major fetal anomaly in the current pregnancy (e.g. gastroschisis, fetal ventriculomegaly, fetal hydronephrosis (>10mm), achondroplasias, fetal congenital heart disease, neural tube defect, sustained fetal arrhythmias)
    """

ans_for_myoma = """
Key Analysis: 
Myomas, also known as fibroids, are benign tumors in the uterus that can cause complications during pregnancy, such as miscarriage, preterm labor, or placental abruption.

Recommendation: 
For Multiple Fibroids: When assessing multiple fibroids, consider their total size. For instance, if there's a 2 cm fibroid and a 3 cm fibroid, the total size is 5 cm, and imaging is as follows:

Moderate (>5 cm) and Large (>10 cm) Fibroids:

    - First-trimester ultrasound CPT® 76801 (plus CPT® 76802 for each additional fetus) if <14 weeks and a complete ultrasound hasn't been done yet.
        - CPT® 76817 for transvaginal ultrasound if the first-trimester ultrasound cannot be completed.
    - Fetal anatomic scan (CPT® 76805 or CPT® 76811 if there's another high-risk indication) if ≥16 weeks.
    - Fetal Anatomy Survey Timing: Ideally, perform fetal anatomy surveys (CPT® 76805/CPT® 76811) between 18 to 22 weeks of gestation. Although they can be done as early as 14 weeks, it's recommended to wait.

    - Lower Uterine Segment or Cervical Fibroid: If the fibroid is in the lower uterine segment or the cervix (cervical fibroid):
        - Ultrasound (CPT® 76815) and/or transvaginal ultrasound (CPT® 76817) every 2 weeks between 16 to 24 weeks.
        - Follow-up ultrasound (CPT® 76816) every 3 to 6 weeks, starting at 23 weeks.
    
For Submucosal Fibroids also follow above Recommendation.
Page Number : 117 of 198
"""
# You are an expert in filtering Ultrasound reports. You get the ultrasound report draft and you create the final version. Your role is to remove unwanted recommendations Based on fetus age in weeks. The rule of thumb is to only include recommendations that are applicable as of now or in future. You should remove all the recommendations which should have been done in the past according to the current fetal age. The fetal age will be given to you. Take a deep breath and work your magic to filter the ultrasound reports."""
filter_by_AUA_prompt = """
[Personality]
I am Fetal Life Bot, an AI assistant to provide helpful information to expectant mothers. I aim to be supportive, empathetic, and knowledgeable regarding pregnancy health. 

[Purpose]
My role is to take ultrasound recommendations for pregnant patients and filter out any advice not applicable to the patient's current stage of pregnancy. This ensures patients only receive relevant guidance for their fetus's gestational age.

[Input]
Ultrasound reports containing various recommendations, along with the fetus's current gestational age in weeks. 

[Output]
Ultrasound recommendations same formate as input tailored to the fetus's developmental stage by removing any advice meant for a younger fetus.
"""


def contains_cpt_code(text):
    # Define a regular expression pattern to match "CPT® XXXXX" where XXXXX is any digit
    pattern = r'CPT® \d{5}'
    
    # Use the re.search function to find the pattern in the text
    match = re.search(pattern, text)
    
    # If a match is found, return True; otherwise, return False
    return bool(match)


class PDFUtils:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()

    def get_context(self,query):
        persist_directory = self.persist_directory
        embedding = self.embedding
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
        docs = vectordb.similarity_search(query,k=2,search_type="similarity")
        return docs

    def get_context_combined(self,docs,AUA):
        context = ""
        page_number = set() 
        for ele in docs:
            json_context = json.loads((ele.page_content.replace("'","\"")))
            # print(json_context['title'])
            page_number.add(json_context['page'])
            # chunk = json.loads(ele.replace("\'","\""))
            final_ans = json_context['title'] + "::\n"
            for key, value in json_context['content'].items():
                f,s = key.split(" ")
                if s == "extra":
                    final_ans += value + "\n"
                elif s == "G":
                    final_ans += value + "\n"
                else:
                    if AUA != None:
                        given_age = int(f)
                        if s == "L" and given_age >= AUA:
                            final_ans += value + "\n"
                        else:
                            continue
                    else:
                        continue

            context += final_ans + "\n\n"
        return context,page_number

    def chat_with_pdf_single_query(self, query):
        reply = ""
        qa_chain_result = self.qa_chain({"question": query, 'chat_history': []}, return_only_outputs=False)
        print("------------------------")
        print(qa_chain_result)
        print("------------------------")
        reply += qa_chain_result["answer"]
        reply += '\nSource Pages : '
        page_set = set()
        for source in qa_chain_result["source_documents"]:
            page_set.add(source.metadata['page']+1) # GPT given pages are always currunt page - 1
        return reply+str(list(page_set))
    
    def chat_with_pdf_q(self,query,AUA,query_context):
        print(query)
        if "Socio-Demographic Risk Factors (maternal age)....................." in query:
            final_ans = ans_for_age
        elif "myoma" in str.lower(query):
            final_ans = ans_for_myoma
        else :
            # prompt_template = """ Your role is to provide a simple short Key Analysis and Recommendations(including CPT Reports) for a specific abnormality ONLY based on the Context provided to you. Please adhere closely to the format of the [Sample Output] and ensure that your response should be concise with Structured bullet point. Do not copy Recommendation from <Sample Output>.
            # [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
            #     1.Do not infer or generate your own answers. Answer questions based solely on provided context. 
            #     2.If you cannot locate the answer within the given <Context>, simply state, "The answer is not found in the provided context."
            #     3.If the key analysis suggests that the condition is considered normal, commonly encountered, common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"

            # [Sample Question 1]
            #     I would like comprehensive guidelines for the AC value 8% if there is any.

            #     Context: 
            #     The ACOG definition of Fetal Growth Restriction (FGR): Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.
            #     Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed - Starting at 23 weeks, a modified BPP (CPT®76815) can be performed once or twice weekly, or Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly, and Starting at 23 weeks Umbilical artery (UA) Doppler (CPT ® 76820) can be performed weekly. If FGR is diagnosed in the current ultrasound, BPP (CPT ® 76818 or CPT® 76819) can be performed if ≥26 weeks, and/or UA Doppler (CPT ® 76820) if ≥23 weeks.

            # [Sample Output 1] 
            #     Key Analysis:   // will contain short key analysis 
            #         • AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.

            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the <Context>.
            #         • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
            #         • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly
            #         • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed weekly


            # [Sample Question 2] 
            #     I would like comprehensive guidelines for Echogenic intracardiac focus (EIF) seen in the left ventricle .if there is any.

            #     Context:
            #         Fetal Echocardiography - Indications for Fetal Conditions::
            #         Initial Fetal echocardiography (CPT® 76825) and/or Doppler echocardiography (CPT® 76827) with or without Doppler color flow velocity mapping (CPT® 93325) can be performed if ≥16 weeks:
            #         Known or suspected abnormal fetal cardiac evaluation on fetal anatomic scan:Known or suspected abnormality must be documented as hard copy or acknowledged verbally by the provider of known or suspected fetal cardiac evaluation.
            #         • Suboptimal cardiac evaluation alone is not an indication for a fetal echogram. If the 4-chamber view is adequate and there is no other suspicion of a cardiac abnormality, a fetal echocardiogram is not considered medically necessary. A follow-up ultrasound (CPT® 76815 or CPT® 76816) is indicated for suboptimal visualization. If the follow-up ultrasound fails to show a 4-chamber view or there is suspicion of a cardiac abnormality, fetal echocardiogram is indicated.
            #         Fetal cardiac arrhythmia; persistent fetal tachycardia or bradycardia.Major fetal extra-cardiac anomaly (excluding soft markers for aneuploidy: for example shortened long bones, pyelectasis, echogenic bowel, hypoplastic nasal bone, cardiac echogenic foci, and choroid plexus cyst).
            #         Congenital heart disease (CHD) in a 1st-degree relative of the fetus (i.e. CHD in the mother, father, or sibling of the fetus).
            #         Known fetal chromosomal abnormalities (fetal aneuploidy) or ultrasound findings of a suspected chromosomal abnormality (excluding soft markers as only ultrasound findings):
                    
            # [Sample Output 2] 
            #     Key Analysis:   // The defintion of abnormality. Does not contains the CPT reports.
            #         • Echogenic intracardiac focus (EIF) is a bright spot seen in the left ventricle of the fetal heart during an ultrasound.
            #         • EIF is a common finding and is considered a soft marker for chromosomal abnormalities, particularly Down syndrome.
            #         • EIF alone is not considered a significant finding and does not typically warrant further testing or intervention.

            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the <Context>.
            #         No Recommendation Needed Cause Finding is Normal


            # [Sample Question 3] 
            #     I would like comprehensive guidelines for Anterior placenta grade 2, partial previa .if there is any.

            #     Context:
            #         Previa (Placenta Previa and Vasa Previa)::
            #         Second and Third Trimesters:For known placenta previa (placental edge covers the internal cervical os) or low lying placenta (placental edge <2 cm from internal os):One routine follow-up ultrasound can be performed in the 3rd trimester (CPT® 76815 or CPT® 76816 and/or CPT® 76817).If placenta previa or low lying placenta is still present, one follow-up ultrasound (CPT® 76815 or CPT® 76816 and/or CPT® 76817) can be performed in 3-4 weeks.If persistent placenta previa (placental edge covers the internal cervical os), BPP (CPT® 76818/CPT® 76819 or modified BPP (CPT® 76815) weekly, starting at 32 weeks.Follow-up ultrasound can be performed at any time if bleeding occurs BPP (CPT® 76818 or CPT® 76819) or CPT® 76815 or CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817).Background and Supporting Information:For pregnancies beyond 16 weeks, if the placental edge is ≥2 cm away from the internal os, the placental location should be reported as normal.If the placental edge is <2 cm from the internal os but not covering the internal os, it should be labeled as low lying.If the placental edge covers the internal cervical os, the placenta should be labeled as a placenta previa.There is no evidence to guide the optimal time of subsequent imaging in pregnancies thought to have placenta previa. In stable patients it is reasonable to perform a follow-up ultrasonogram at approximately 32 weeks of gestation and an additional study at 36 weeks of gestation (if the previa persists) to determine the optimal route and timing of delivery. There is no clear benefit from more frequent ultrasonograms (eg, every 4 weeks) in stable cases.
            #         Vasa Previa:Vasa previa occurs when fetal blood vessels that are unprotected by the umbilical cord or placenta run through the amniotic membranes and cross over the internal cervical os.If a Vasa Previa is found on initial imaging:
            #         Detailed anatomic ultrasound at ≥16 weeks:The fetal anatomy survey (CPT® 76805/CPT® 76811) is optimally performed at 18 to 22 weeks of gestation, though it can be conducted as early as 14 weeks gestation, per ACOG guidelines.
                      
            # [Sample Output 3] 
            #     Key Analysis:   // The defintion of abnormality. Does not contains the CPT reports.
            #         The answer is not found in the provided context.
            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the [Context].
            #         The answer is not found in the provided context.

                                        
            # [Context]

            # <context>
            # """

            # prompt_template = """ Your role is to provide a short Key Analysis(will contain a short 10-20 word Analysis) and Recommendations (including CPT Reports) for a specific abnormality ONLY based on the Context provided to you. Please adhere closely to the format of the [Sample Output] and ensure that your response should be concise with Structured bullet point. Do not copy Recommendation from <Sample Output>.
            # [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
            #     1.Do not infer or generate your own answers. Answer questions based solely on provided context. 
            #     2.If you cannot locate the answer within the given <Context>, simply state, "The answer is not found in the provided context."
            #     3.If the key analysis suggests that the condition is considered normal, commonly encountered, common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"

            # [Sample Question 1]
            #     I would like comprehensive guidelines for the AC value 8% if there is any.

            #     Context: 
            #     The ACOG definition of Fetal Growth Restriction (FGR): Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.
            #     Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed - Starting at 23 weeks, a modified BPP (CPT®76815) can be performed once or twice weekly, or Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly, and Starting at 23 weeks Umbilical artery (UA) Doppler (CPT ® 76820) can be performed weekly. If FGR is diagnosed in the current ultrasound, BPP (CPT ® 76818 or CPT® 76819) can be performed if ≥26 weeks, and/or UA Doppler (CPT ® 76820) if ≥23 weeks.

            # [Sample Output 1] 
            #     Key Analysis:   // will contain a short 10-20 word Analysis
            #         • Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.

            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the [Context].
            #         • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
            #         • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly
            #         • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed weekly


            # [Sample Question 2] 
            #     I would like comprehensive guidelines for Echogenic intracardiac focus (EIF) seen in the left ventricle .if there is any.

            #     Context:
            #         Fetal Echocardiography - Indications for Fetal Conditions::
            #         Initial Fetal echocardiography (CPT® 76825) and/or Doppler echocardiography (CPT® 76827) with or without Doppler color flow velocity mapping (CPT® 93325) can be performed if ≥16 weeks:
            #         Known or suspected abnormal fetal cardiac evaluation on fetal anatomic scan:Known or suspected abnormality must be documented as hard copy or acknowledged verbally by the provider of known or suspected fetal cardiac evaluation.
            #         • Suboptimal cardiac evaluation alone is not an indication for a fetal echogram. If the 4-chamber view is adequate and there is no other suspicion of a cardiac abnormality, a fetal echocardiogram is not considered medically necessary. A follow-up ultrasound (CPT® 76815 or CPT® 76816) is indicated for suboptimal visualization. If the follow-up ultrasound fails to show a 4-chamber view or there is suspicion of a cardiac abnormality, fetal echocardiogram is indicated.
            #         Fetal cardiac arrhythmia; persistent fetal tachycardia or bradycardia.Major fetal extra-cardiac anomaly (excluding soft markers for aneuploidy: for example shortened long bones, pyelectasis, echogenic bowel, hypoplastic nasal bone, cardiac echogenic foci, and choroid plexus cyst).
            #         Congenital heart disease (CHD) in a 1st-degree relative of the fetus (i.e. CHD in the mother, father, or sibling of the fetus).
            #         Known fetal chromosomal abnormalities (fetal aneuploidy) or ultrasound findings of a suspected chromosomal abnormality (excluding soft markers as only ultrasound findings):
                    
            # [Sample Output 2] 
            #     Key Analysis:   // will contain a short 10-20 word Analysis
            #         • Echogenic intracardiac focus (EIF) is a bright spot seen in the left ventricle of the fetal heart during an ultrasound.
            #         • EIF is a common finding and is considered a soft marker for chromosomal abnormalities, particularly Down syndrome.
            #         • EIF alone is not considered a significant finding and does not typically warrant further testing or intervention.

            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the [Context].
            #         No Recommendation Needed Cause Finding is Normal


            # [Sample Question 3] 
            #     I would like comprehensive guidelines for Anterior placenta grade 2, partial previa .if there is any.

            #     Context:
            #         Previa (Placenta Previa and Vasa Previa)::
            #         Second and Third Trimesters:For known placenta previa (placental edge covers the internal cervical os) or low lying placenta (placental edge <2 cm from internal os):One routine follow-up ultrasound can be performed in the 3rd trimester (CPT® 76815 or CPT® 76816 and/or CPT® 76817).If placenta previa or low lying placenta is still present, one follow-up ultrasound (CPT® 76815 or CPT® 76816 and/or CPT® 76817) can be performed in 3-4 weeks.If persistent placenta previa (placental edge covers the internal cervical os), BPP (CPT® 76818/CPT® 76819 or modified BPP (CPT® 76815) weekly, starting at 32 weeks.Follow-up ultrasound can be performed at any time if bleeding occurs BPP (CPT® 76818 or CPT® 76819) or CPT® 76815 or CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817).Background and Supporting Information:For pregnancies beyond 16 weeks, if the placental edge is ≥2 cm away from the internal os, the placental location should be reported as normal.If the placental edge is <2 cm from the internal os but not covering the internal os, it should be labeled as low lying.If the placental edge covers the internal cervical os, the placenta should be labeled as a placenta previa.There is no evidence to guide the optimal time of subsequent imaging in pregnancies thought to have placenta previa. In stable patients it is reasonable to perform a follow-up ultrasonogram at approximately 32 weeks of gestation and an additional study at 36 weeks of gestation (if the previa persists) to determine the optimal route and timing of delivery. There is no clear benefit from more frequent ultrasonograms (eg, every 4 weeks) in stable cases.
            #         Vasa Previa:Vasa previa occurs when fetal blood vessels that are unprotected by the umbilical cord or placenta run through the amniotic membranes and cross over the internal cervical os.If a Vasa Previa is found on initial imaging:
            #         Detailed anatomic ultrasound at ≥16 weeks:The fetal anatomy survey (CPT® 76805/CPT® 76811) is optimally performed at 18 to 22 weeks of gestation, though it can be conducted as early as 14 weeks gestation, per ACOG guidelines.
                      
            # [Sample Output 3] 
            #     Key Analysis:   // will contain a short 10-20 word Analysis
            #         The answer is not found in the provided context.
            #     Recommendation: // will contain comprehensive guidelines with CPT reports from the [Context].
            #         The answer is not found in the provided context.

                                        
            # [Context]

            # <context>
            # """

            prompt_template = """ Your role is to provide a short Key Analysis and Recommendations (including CPT Reports) for a specific abnormality ONLY based on the Context provided to you. Please adhere closely to the format of the [Sample Output] and ensure that your response should be concise with Structured bullet point. Do not copy Recommendation from <Sample Output>.
            [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
                1.Do not infer or generate your own answers. Answer questions based solely on provided context. 
                2.If you cannot locate the answer within the given <Context>, simply state, "The answer is not found in the provided context."
                3.If the key analysis suggests that the condition is considered normal, commonly encountered, common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"

            [Sample Question 1]
                I would like comprehensive guidelines for the AC value 8% if there is any.

                Context: 
                The ACOG definition of Fetal Growth Restriction (FGR): Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.
                Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed - Starting at 23 weeks, a modified BPP (CPT®76815) can be performed once or twice weekly, or Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly, and Starting at 23 weeks Umbilical artery (UA) Doppler (CPT ® 76820) can be performed weekly. If FGR is diagnosed in the current ultrasound, BPP (CPT ® 76818 or CPT® 76819) can be performed if ≥26 weeks, and/or UA Doppler (CPT ® 76820) if ≥23 weeks.

            [Sample Output 1] 
                Key Analysis:   // explain single line defination of abnormality from user Query  
                    • AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal Circumference ≤10th percentile.

                Recommendation: // will contain comprehensive guideline from the [Context].
                    • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
                    • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815) can be performed once or twice weekly
                    • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed weekly


            [Sample Question 2] 
                I would like comprehensive guidelines for Echogenic intracardiac focus (EIF) seen in the left ventricle .if there is any.

                Context:
                    Fetal Echocardiography - Indications for Fetal Conditions::
                    Initial Fetal echocardiography (CPT® 76825) and/or Doppler echocardiography (CPT® 76827) with or without Doppler color flow velocity mapping (CPT® 93325) can be performed if ≥16 weeks:
                    Known or suspected abnormal fetal cardiac evaluation on fetal anatomic scan:Known or suspected abnormality must be documented as hard copy or acknowledged verbally by the provider of known or suspected fetal cardiac evaluation.
                    • Suboptimal cardiac evaluation alone is not an indication for a fetal echogram. If the 4-chamber view is adequate and there is no other suspicion of a cardiac abnormality, a fetal echocardiogram is not considered medically necessary. A follow-up ultrasound (CPT® 76815 or CPT® 76816) is indicated for suboptimal visualization. If the follow-up ultrasound fails to show a 4-chamber view or there is suspicion of a cardiac abnormality, fetal echocardiogram is indicated.
                    Fetal cardiac arrhythmia; persistent fetal tachycardia or bradycardia.Major fetal extra-cardiac anomaly (excluding soft markers for aneuploidy: for example shortened long bones, pyelectasis, echogenic bowel, hypoplastic nasal bone, cardiac echogenic foci, and choroid plexus cyst).
                    Congenital heart disease (CHD) in a 1st-degree relative of the fetus (i.e. CHD in the mother, father, or sibling of the fetus).
                    Known fetal chromosomal abnormalities (fetal aneuploidy) or ultrasound findings of a suspected chromosomal abnormality (excluding soft markers as only ultrasound findings):
                    
            [Sample Output 2]
                Key Analysis:   // explain single line defination of abnormality from user Query
                    • Echogenic intracardiac focus (EIF) is a bright spot seen in the left ventricle of the fetal heart during an ultrasound.
                    • EIF is a common finding and is considered a soft marker for chromosomal abnormalities, particularly Down syndrome.
                    • EIF alone is not considered a significant finding and does not typically warrant further testing or intervention.

                Recommendation: 
                    No Recommendation Needed Cause Finding is Normal


            [Sample Question 3] 
                I would like comprehensive guidelines for Anterior placenta grade 2, partial previa .if there is any.

                Context:
                    Previa (Placenta Previa and Vasa Previa)::
                    Second and Third Trimesters:For known placenta previa (placental edge covers the internal cervical os) or low lying placenta (placental edge <2 cm from internal os):One routine follow-up ultrasound can be performed in the 3rd trimester (CPT® 76815 or CPT® 76816 and/or CPT® 76817).If placenta previa or low lying placenta is still present, one follow-up ultrasound (CPT® 76815 or CPT® 76816 and/or CPT® 76817) can be performed in 3-4 weeks.If persistent placenta previa (placental edge covers the internal cervical os), BPP (CPT® 76818/CPT® 76819 or modified BPP (CPT® 76815) weekly, starting at 32 weeks.Follow-up ultrasound can be performed at any time if bleeding occurs BPP (CPT® 76818 or CPT® 76819) or CPT® 76815 or CPT® 76816 if a complete ultrasound was done previously and/or CPT® 76817).Background and Supporting Information:For pregnancies beyond 16 weeks, if the placental edge is ≥2 cm away from the internal os, the placental location should be reported as normal.If the placental edge is <2 cm from the internal os but not covering the internal os, it should be labeled as low lying.If the placental edge covers the internal cervical os, the placenta should be labeled as a placenta previa.There is no evidence to guide the optimal time of subsequent imaging in pregnancies thought to have placenta previa. In stable patients it is reasonable to perform a follow-up ultrasonogram at approximately 32 weeks of gestation and an additional study at 36 weeks of gestation (if the previa persists) to determine the optimal route and timing of delivery. There is no clear benefit from more frequent ultrasonograms (eg, every 4 weeks) in stable cases.
                    Vasa Previa:Vasa previa occurs when fetal blood vessels that are unprotected by the umbilical cord or placenta run through the amniotic membranes and cross over the internal cervical os.If a Vasa Previa is found on initial imaging:
                    Detailed anatomic ultrasound at ≥16 weeks:The fetal anatomy survey (CPT® 76805/CPT® 76811) is optimally performed at 18 to 22 weeks of gestation, though it can be conducted as early as 14 weeks gestation, per ACOG guidelines.
                      
            [Sample Output 3] 
                Key Analysis:   // explain single line defination of abnormality from user Query
                    The answer is not found in the provided context.
                Recommendation: 
                    The answer is not found in the provided context.
                                        
            [Context]

            <context>
            """
            
            results = self.get_context(query_context)
            print("below is results.................s")
            print(results)
            print("..............................")
            context,page = self.get_context_combined(results,AUA)
            print("here is the context..........................................................................................................")
            print(context)
            print("..........................................................................................................")
            history = [{"role": "system", "content": prompt_template.replace("<context>",context)},{"role": "user", "content": f"{query}" }]
            try:
                final_ans = get_completion(history)
            except Exception as e :
                try:
                    final_ans = get_completion(history)
                except Exception as e :
                    final_ans = str(e) + "\n\n Appologies! curruntly we are getting issue from OpenAI.\nplease try again after some time."
                # final_ans = str(e) + "\n\n Appologies! curruntly we are getting issue from OpenAI.\nplease try again after some time."
            print(f"page number is {page}")
            final_ans += "\nPage : "+str(page)
            print("below is the rough answer.......")
            print(final_ans)
            print(".................................................\n")
            contain_cpt_reports = contains_cpt_code(final_ans)
            print(f"contain cpt reports : {contain_cpt_reports}")
            if not contain_cpt_reports:
                final_ans = " "


        try:
            if len(final_ans.split("Recommendation:")[1].strip())<110:
                if "The answer is not found in the provided context." in final_ans or "No Recommendation Needed Cause Finding is Normal" in final_ans:
                    final_ans = " "
                    # AUA = None
        except Exception as e:
            pass
        print("\nBelow is the final answer.......................>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        print(final_ans)
        print("\n\n")

        return final_ans

# Use When you want to create a db
# pdf_folder_path = "ChatBotUI/static/pdf"
# persist_directory = "./db"

# # Create an instance of PDFUtils class
# pdf_utils = PDFUtils(pdf_folder_path, persist_directory)
# pdf_utils.initialize_qa_chain()
# query = "I would like comprehensive guidelines for the " + "placenta previa"  + " along with CPT reports.\n"
# result = pdf_utils.chat_with_pdf_q(query)
# print(result)

# # Call the initialize_qa_chain method to initialize the QA chain
# pdf_utils.create_vector_db_from_pdfs()


# pdf_utils = PDFUtils()