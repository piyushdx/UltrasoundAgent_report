# import json
# import streamlit as st
# from dotenv import load_dotenv
# from PyPDF2 import PdfReader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chat_models import ChatOpenAI
# from langchain import LLMChain
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain, RetrievalQA
# from htmlTemplates import css, bot_template, user_template
# from langchain.llms import HuggingFaceHub
# from langchain.document_loaders import PyPDFLoader
# from langchain.chains.combine_documents.stuff import StuffDocumentsChain
# from prompts import qa_template
# from langchain.prompts import PromptTemplate


# def get_pdf_text(pdf_docs):
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     return text

# def get_text_chunks(text):
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(text)
#     return chunks


# def get_vectorstore(text_chunks):
#     embeddings = HuggingFaceEmbeddings(
#         model_name='sentence-transformers/all-MiniLM-L6-v2')

#     vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
#     return vectorstore

# def set_qa_prompt():
#     """
#     Prompt template for QA retrieval for each vectorstore
#     """
#     prompt = PromptTemplate(template=qa_template,
#                             input_variables=['context', 'question'])
#     return prompt

# def get_conversation_chain(vectorstore, qa_prompt):
#     repo_id = "meta-llama/Llama-2-70b-chat-hf"
#     llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={
#                          "temperature": 0.2, "max_seq_len": 4000, "max_new_tokens": 2048})
#     memory = ConversationBufferMemory(
#         memory_key='chat_history', return_messages=True)
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         memory=memory,
#         combine_docs_chain_kwargs={"prompt": qa_prompt}
#     )
#     return conversation_chain

# def handle_userinput(user_question):
# #    print(f"Sending user question to LLM: {user_question}")  
#     response = st.session_state.conversation({'question': user_question})
# #    print(f"Received response from LLM: {response}")  

#     st.session_state.chat_history = response['chat_history']

#     for i, message in enumerate(st.session_state.chat_history):
#         if i % 2 == 0:  # User's messages
#             st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
#         else:  # LLM's responses
#             st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


# def main():
#     load_dotenv()
#     st.set_page_config(page_title="Chat and Summarize",
#                        page_icon=":diamond_shape_with_a_dot_inside:")
#     st.write(css, unsafe_allow_html=True)

#     if "conversation" not in st.session_state:
#         st.session_state.conversation = None
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = None

#     st.header("Chat and Summarize (Powered by llama 2) :diamond_shape_with_a_dot_inside:")
#     user_question = st.text_input("Ask a question about your documents:")
#     if user_question:
#         handle_userinput(user_question)

#     with st.sidebar:
#         st.subheader("Your documents 📎")
#         pdf_docs = st.file_uploader(
#             "Upload your PDFs here and click on 'Process'", accept_multiple_files=True, type="pdf")
#         if st.button("Process :mag:"):
#             with st.spinner("Processing"):
#                 raw_text = get_pdf_text(pdf_docs)
#                 text_chunks = get_text_chunks(raw_text)
#                 vectorstore = get_vectorstore(text_chunks)
#                 qa_prompt = set_qa_prompt()
#                 st.session_state.conversation = get_conversation_chain(vectorstore, qa_prompt)

#         if st.button("Summarize :bookmark_tabs:"):
#             with st.spinner("Summarizing..."):
#                 # This line will send the "summarize the pdf" question through the regular chat flow
#                 handle_userinput("summarize the pdf")

# if __name__ == '__main__':
#     main()


# import difflib
# import re

# def remove_duplicate(text):
#     del1 = "Here are some noteworthy findings (abnormalities) along with corresponding CPT reports that could provide useful information to you."
#     del2 = "Please feel free to ask me any specific questions you have regarding the report. I'm here to help!😊"
#     try:
#         text.remove(del1)
#         text.remove(del2)
#     except Exception as e:
#         pass
#     new_text = []
#     remaining_list = {}
#     for i in range(len(text)):
#         if len(text[i]) > 120:
#             new_text.append(text[i][100:])
#         else:
#             remaining_list[str(i)] = text[i]



#     def is_similar(a, b, threshold=0.45):
#         """
#         Determine if two strings are similar based on the difflib ratio.
#         """
#         ratio = difflib.SequenceMatcher(None, a, b).ratio()
#         print(ratio)
#         return ratio >= threshold

#     def remove_duplicates(input_list):
#         unique_list = []
#         for item in input_list:
#             is_duplicate = False
#             for unique_item in unique_list:
#                 if is_similar(item, unique_item):
#                     is_duplicate = True
#                     break
#             if not is_duplicate:
#                 unique_list.append(item)
#         return unique_list

#     unique_text = remove_duplicates(new_text)

#     final_answer = []
#     for tex in text:
#         for item in unique_text:
#             if str(item[:19]) == str(tex[100:119]):
#                 print(item[:19])
#                 print(tex[100:119])
#                 final_answer.append(tex)

#     if any(remaining_list):
#         print("yes found in json")
#         for key,value in remaining_list.items():
#             final_answer.insert(int(key),value)
#     final_answer.insert(0,del1)
#     final_answer.append(del2)
#     return final_answer


# def is_similar(a, b, threshold=0.45):
#     """
#     Determine if two strings are similar based on the difflib ratio.
#     """
#     ratio = difflib.SequenceMatcher(None, a, b).ratio()
#     print(ratio)
#     return ratio >= threshold

# is_similar("Known Macrosomia ≥90th percentile EFW 93.42% is defined as an estimated fetal weight greater than the 90th percentile for gestational age.","Polyhydramnios is confirmed when the Amniotic Fluid Index (AFI) is ≥24cm or the maximum vertical pocket (MVP) is ≥8cm.")

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# # Define your two text strings
# text1 = "AFI ≥24cm or maximum vertical pocket (MVP) ≥8cm indicates polyhydramnios."
# text2 = "Polyhydramnios is confirmed when the Amniotic Fluid Index (AFI) is ≥24cm or the maximum vertical pocket (MVP) is ≥8cm."

# # Create a TF-IDF vectorizer
# vectorizer = TfidfVectorizer()

# # Fit and transform the text strings into TF-IDF vectors
# tfidf_matrix = vectorizer.fit_transform([text1, text2])

# # Calculate the cosine similarity between the vectors
# cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

# # The result will be a 2D array, so you can extract the similarity value
# similarity = cosine_sim[0][0]

# print(f"Cosine Similarity: {similarity}")

# def remove_duplicate_using_key_analysis(final_response):
#     def get_key_analysis(final_response,key_json={}):
#         # Use regular expressions to extract Key Analysis and Recommendations
#         for i in range(len(final_response)):
#             key_analysis_match = re.search(r'Key Analysis:(.*?)Recommendation:', final_response[i], re.DOTALL | re.IGNORECASE)
#             key_analysis = key_analysis_match.group(1).strip() if key_analysis_match else ""
#             if key_analysis != "":
#                 key_json[str(i)] = key_analysis

#         return key_json

#     def is_similar(a, b, threshold=0.45):
#         """
#         Determine if two strings are similar based on the difflib ratio.
#         """
#         ratio = difflib.SequenceMatcher(None, a, b).ratio()
#         print(ratio)
#         return ratio >= threshold

#     def remove_duplicates(input_list):
#         unique_list = []
#         for item in input_list:
#             is_duplicate = False
#             for unique_item in unique_list:
#                 if is_similar(item, unique_item):
#                     is_duplicate = True
#                     break
#             if not is_duplicate:
#                 unique_list.append(item)
#         return unique_list
#     try:
#         json_data = get_key_analysis(final_response)
#         value_list = remove_duplicates(list(json_data.values()))

#         # Initialize a list to store keys
#         keys_not_in_list = []

#         # Iterate through the dictionary and check if the value is not in the value_list
#         for key, value in json_data.items():
#             if value not in value_list:
#                 keys_not_in_list.append(key)
#         for i in keys_not_in_list:
#             final_response.pop(int(i))
#     except Exception as e:
#         pass
    
#     return final_response
# import re

# def contains_cpt_code(text):
#     # Define a regular expression pattern to match "CPT® XXXXX" where XXXXX is any digit
#     pattern = r'CPT® \d{5}'
    
#     # Use the re.search function to find the pattern in the text
#     match = re.search(pattern, text)
    
#     # If a match is found, return True; otherwise, return False
#     return bool(match)

# text = """Unable to obtain profile view :

# Key Analysis: Unable to obtain profile view is a technical difficulty encountered during the ultrasound examination, which may limit the assessment of fetal anatomy.

# Recommendation:
# - Repeat the ultrasound examination to obtain a profile view if clinically indicated.
# - Consider using alternative imaging techniques such as transvaginal ultrasound or three-dimensional ultrasound to assess fetal anatomy.
# - Consult with a specialist or experienced sonographer for further evaluation and guidance.
# - No specific CPT reports are mentioned in the context."""

# print(contains_cpt_code(text))



# import ast
# # from nltk.corpus import wordnet

# text = "{'Fetal Position': 'Breech', 'Facial Profile': 'Not seen', 'Feet': 'Not seen', '4 Chamber': 'Not seen', 'Lt. Outflow Tract': 'Not seen', 'Rt. Qutflow Tract': 'Not seen', 'Spine': 'Not seen', 'Known Macrosomia ≥90th percentile': 'EFW is 16.32 pctl', 'Breech presentation': '', 'Small for gestational age (SGA)': '', 'Unable to obtain profile views': '', 'Short cervical length': ''}"

# data = ast.literal_eval(text)
# # unique_data = {}
# final_list = []
# for key, value in data.items():
#     if value == "Not seen":
#         pass
#     else:
#         combined = key + " " + value
#         final_list.append(combined)
# print(final_list)  


#     for syn in wordnet.synsets(combined): 
#         for lemma in syn.lemmas():
#             synonyms.add(lemma.name())
            
#     if not any(syn in unique_data for syn in synonyms):
#         unique_data[key] = value

# print(unique_data)


# def remove_duplicate_using_Recommendation(final_list):
#     def is_similar(a, b, threshold=0.45):
#         """
#         Determine if two strings are similar based on the difflib ratio.
#         """
#         ratio = difflib.SequenceMatcher(None, a, b).ratio()
#         print(f'{a},{b}:{ratio}')
#         return ratio >= threshold

#     def remove_duplicates(input_list):
#         unique_list = []
#         for item in input_list:
#             is_duplicate = False
#             for unique_item in unique_list:
#                 if is_similar(item, unique_item):
#                     is_duplicate = True
#                     break
#             if not is_duplicate:
#                 unique_list.append(item)
#         return unique_list
    
#     try:
#         value_list = remove_duplicates(final_list)
#         print(value_list)
#         # # Initialize a list to store keys
#         # keys_not_in_list = []

#         # # Iterate through the dictionary and check if the value is not in the value_list
#         # for key, value in json_data.items():
#         #     if value not in value_list:
#         #         keys_not_in_list.append(key)
#         # for i in keys_not_in_list:
#         #     final_list.pop(int(i))
#     except Exception as e:
#         pass
    
#     return final_list

# remove_duplicate_using_Recommendation(final_list)

# from flask import Flask, render_template, request, Response
# import openai
# from flask import jsonify
# import os
# import openai
# import json
# from langchain.embeddings import OpenAIEmbeddings
# # from langchain.vectorstores import Chroma
# from pdf_utils import PDFUtils

# from insights import insightsAll

# abnormalities = {'Fetal Position': 'Breech', 'Known Macrosomia ≥90th percentile': 'EFW is 76.87 pctl', 'Breech presentation': 'yes', 'Mild pyelectasis': '', 'right kidney': 'unseen', 'Suboptimal cardiac views': '', 'Unable to obtain optimal ACI and spine views': '', 'Short and closed cervix': ''}

# def get_completion(prompt, model="gpt-3.5-turbo"):
#     # messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=prompt,
#         temperature=0.2  # this is the degree of randomness of the model's output
#     )
#     return response.choices[0].message["content"]

# def extract_content_in_braces(text):
#     # Find the first opening brace from the left
#     left_brace_index = text.find("[")
    
#     # Find the first closing brace from the right
#     right_brace_index = text.rfind("]")
    
#     if left_brace_index != -1 and right_brace_index != -1 and left_brace_index < right_brace_index:
#         # Extract the content within the curly braces
#         content_between_braces = text[left_brace_index:right_brace_index+1].strip()
#         return content_between_braces
#     else:
#         return None

# def find_indices_of_difference(old_list, new_list):
#     # Find the indices of elements in old_list that are not in new_list
#     indices_of_difference = [i for i, item in enumerate(old_list) if item.strip() not in new_list]
#     return indices_of_difference

# def remove_elements_by_indices(indices, data):
#     # Create a new dictionary with elements removed at specified indices
#     updated_data = {key: value for i, (key, value) in enumerate(data.items()) if i not in indices}
#     return updated_data

# def remove_similar(abnormalities):
#     print(abnormalities)
#     old_list = [f"{key} {value}" for key, value in abnormalities.items()]
#     print(old_list)
#     try:
#         output = get_completion([{"role": "system", "content": """use with give you a Abnormality List. Remove abnormalities from the provided list that mean the same. Output only the final list and nothing else."""}, {
#                                          "role": "user", "content": "Abnormality List: "+str(old_list)}])
#         print(output)
#         new_list = extract_content_in_braces(output)
#         print(new_list)
#         indices = find_indices_of_difference(old_list, new_list)
#         print(indices)
#         abnormalities = remove_elements_by_indices(indices, abnormalities)
#     except Exception as e:
#         return abnormalities    
#     return abnormalities


# print(remove_similar(abnormalities))

# ['Fetal Position Breech', 'Known Macrosomia ≥90th percentile EFW is 76.87 pctl', 'Breech presentation yes', 'Mild pyelectasis ', 'right kidney unseen', 'Suboptimal cardiac views ', 'Unable to obtain optimal ACI and spine views ', 'Short and closed cervix ']
# ['Fetal Position Breech', 'Known Macrosomia ≥90th percentile EFW is 76.87 pctl', 'Mild pyelectasis', 'right kidney unseen', 'Suboptimal cardiac views', 'Unable to obtain optimal ACI and spine views', 'Short and closed cervix']

# sys_prompt = """
# Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.
# [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
#     1.Answer questions based solely on provided context. do not infer or generate your own answers.
#     2.Only If above context does not contain relevant answer with CPT reports for Below <Question>, then only, simply say and only say following... Recommendation: "No specific CPT reports are mentioned in the context". But if context contain answer then give recommendations only.
#     3.If the key analysis suggests that the condition is normal, commonly encountered,common finding or benign, your response should simply say and only say following... Recommendation: "No Recommendation Needed Cause Findind is Normal"
#     4.find page number from context and show as sample output.

# [Sample Output]
#     Key Analysis: //will solely consist of an explanation of the analysis. 
#     Recommendation: //will include all the CPT reports in detail and guidelines, as demonstrated in the <Sample Output>.
#     Page Number : //will show page number from Context

# [Sample Question]
#     I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
# [Sample Output] 
#     Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
#         actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
#         Circumference ≤10th percentile.
#     Recommendation:
#          Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
#          Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
#         can be performed once or twice weekly
#          Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
#         weekly
#          Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
#         performed every 2 to 4 weeks if complete anatomy ultrasound previously performed
#     Page Number : 146 of 198

# Remember <STRICT RULES TO FOLLOW WHILE GIVING ANSWER> and <Sample Output>

# Context : 
#     Adnexal Mass 
#         • For a known or suspected adnexal/pelvic mass, perform:
#             Complete first trimester ultrasound CPT® 76801 [plus CPT® 76802 for each
#             additional fetus] if <14 weeks and a complete ultrasound has not yet been
#             performed, and/or CPT® 76817 for a transvaginal ultrasound
#             CPT® 76801 is preferred for dating, but if this is unable to be completed
#             then CPT® 76815 and/or CPT® 76817 for a transvaginal ultrasound is
#             indicated
#             CPT® 76805 [plus CPT® 76810 if more than one fetus] if a complete fetal
#             anatomic scan has not yet been performed and ≥14 weeks, or
#             CPT® 76816 if a complete anatomy scan was done previously and/or CPT ®
#             76817 if poor visualization of the adnexal mass.
#         • Following the initial ultrasound, follow up can be done once in each trimester
#             CPT® 76805 [plus CPT® 76810 for each additional fetus] if a complete fetal
#             anatomic scan has not yet been performed, or
#             CPT® 76815 or CPT® 76816 if a complete ultrasound was previously
#             performed.
#             CPT® 76817 if poor visualization of the adnexal mass
#         •MRI Pelvis (CPT® 72195) without contrast can be done for indeterminate findings on ultrasound; for surgical planning and/or for suspected malignancy.
#         •See Adnexal Mass/Ovarian Cysts (PV-5) in the Pelvis Imaging Guidelines

#     Background and Supporting Information
#         The majority of adnexal masses in pregnancy are benign, the most common
#         diagnoses are mature teratomas and corpus luteum or paraovarian cysts.
#         Malignancy is reported in only 1.2-6.8% of pregnant patients with persistent mass.
#         Levels of CA-125 are elevated in pregnancy, a low-level elevation in pregnancy is
#         not typically associated with malignancy.
#         ACOG recommendations for imaging during pregnancy and lactation:
#         o Ultrasonography and magnetic resonance imaging (MRI) are not associated
#         with risk and are the imaging techniques of choice for the pregnant patient, but
#         they should be used prudently and only when use is expected to answer a
#         relevant clinical question or otherwise provide medical benefit to the patient.

# Remember <STRICT RULES TO FOLLOW WHILE GIVING ANSWER> and <Sample Output>
# """
# output = get_completion([{"role": "system", "content": sys_prompt}, {"role": "user", "content": "I would like comprehensive guidelines for the Fetal position breech along with CPT reports.if there is any."}])
# print(output)

# AUA = 15

# filter_by_AUA_prompt = f"""
# You excel at filtering ultrasound report recommendations. Take a moment to review each recommendation line, and if it indicates < {AUA} weeks, remove it; otherwise, keep everything else as it is and provide the resulting output. 
# """

# filter_by_AUA_prompt = """
# You excel at filtering ultrasound report recommendations. Take a moment to review each recommendation line, and if it indicates a gestational age of less than {AUA} weeks, remove it; otherwise, keep everything as it is and provide the resulting output.
# """

# final_ans = """
# To confirm suspected abnormal fetal position or presentation (transverse or breech
# presentation) at ≥36 weeks gestation, report one of the following:
# o CPT® 76805 (plus CPT® 76810 for each additional fetus) when complete
# anatomy scan has not yet been performed in the pregnancy or
# o CPT® 76815 for limited ultrasound to check fetal position or
# o CPT® 76816 if version is being considered and/or for delivery planning
# """

# filter_by_AUA_prompt = f"""
# show all the remaining information after eliminate recommendations intended to do CPT report <14 weeks.
# """


# final_ans = """
# - Complete first trimester ultrasound CPT® 76801 [plus CPT® 76802 for each additional fetus] if <14 weeks and a complete ultrasound has not yet been performed, and/or CPT® 76817 for a transvaginal ultrasound
# - CPT® 76801 is preferred for dating, but if this is unable to be completed then
# - CPT® 76815 and/or CPT® 76817 for a transvaginal ultrasound is indicated
# - See Detailed First Trimester Fetal Anatomic Scan (OB-9.12) for indications for detailed first trimester fetal anatomic evaluation 5,6
# - Detailed Fetal Anatomic Scan CPT® 76811 if ≥16 weeks
# - Though CPT® 76811 can be performed as early as 14 weeks gestation, per ACOG, in the absence of other specific indications, it is optimally performed at 18 to 22 weeks of gestation
# - Starting at 23 follow-up growth scans (CPT® 76816) every 3 to 6 weeks
# - BPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815), weekly starting at 32 weeks
# - More frequent antepartum fetal surveillance can be performed as stipulated below:
# - Starting at 32 weeks, perform BPP (CPT® 76818 or CPT® 76819) or modified BPP (CPT® 76815) up to 2x weekly for the conditions below:
# - Antiphospholipid Syndrome
# - Maternal Renal Disease (moderate to severe with creatinine >1.4mg/dl)
# - Sickle cell disease
# - Starting at diagnosis perform BPP (CPT® 76818 or CPT® 76819) if ≥26 weeks, or modified BPP (CPT® 76815) if ≥23 weeks, up to 2x weekly:
# - Intra-hepatic cholestasis of pregnancy (IHCP)
# - Complicated Sickle cell disease (e.g. co-existing hypertension, vaso-occlusive crisis, fetal growth restriction)
# - Complicated SLE (e.g. active lupus nephritis, or recent flares)
# - Major fetal anomaly in the current pregnancy (e.g. gastroschisis, fetal ventriculomegaly, fetal hydronephrosis (>10mm), achondroplasias, fetal congenital heart disease, neural tube defect, sustained fetal arrhythmias)
# """

# final_ans = """
# If more than one fibroid, total size of all fibroids should be used, i.e. one fibroid at 2 cm and one 3 cm is total of 5 cm and imaging would be indicated as below:
# o Moderate (>5 cm) and large (>10 cm) fibroid(s):
# - Complete first trimester ultrasound CPT® 76801 [plus CPT® 76802 for each additional fetus] if <14 weeks and a complete ultrasound has not yet been performed, and/or CPT® 76817 for a transvaginal ultrasound
# - CPT® 76801 is preferred for dating, but if this is unable to be completed then CPT® 76815 and/or CPT® 76817 for a transvaginal ultrasound is indicated
# - Fetal anatomic scan (CPT® 76805 or CPT® 76811 if other high risk indication. See High Risk Pregnancy (OB-9)) if ≥16 weeks.
# - Though fetal anatomy survey (CPT® 76805/CPT® 76811) can be performed as early as 14 weeks gestation, per ACOG, in the absence of other specific indications, it is optimally performed at 18 to 22 weeks of gestation.
# - If the fibroid is in the lower uterine segment or the cervix (cervical fibroid), can perform ultrasound (CPT® 76815) and/or transvaginal ultrasound (CPT ® 76817) every 2 weeks between 16 to 24 weeks, and
# - Follow up ultrasound (CPT® 76816) every 3 to 6 weeks, starting at 23 weeks.
# """



# filter_by_AUA_prompt = """Process the provided recommendation of CPT reports individually. think step by step and Remove any individual recommendation that are intended for an age less than {AUA} weeks. then return a json in below formate.
# final_ans = {
# important_results = "<result>" // <result> will be remaining output
# }
# """

# history = [{"role": "system", "content": "you are ultrasound report agent."},{"role": "assistant", "content": filter_by_AUA_prompt},{"role": "user", "content": final_ans}]

# if AUA is not None:
# filter_by_AUA_prompt = f"""
# show all the remaining information after eliminate recommendations intended to do CPT report <14 weeks.
# """
#     prompt_filter_fetus_age = [{"role": "system", "content":filter_by_AUA_prompt},{"role":"user", "content": f"""The ultrasound report is as follows:""" + "\n" + final_ans}]
#     # final_ans = get_completion(history)
#     final_ans = get_completion(prompt_filter_fetus_age)
# print(final_ans)


# import re

# text = """
# Known fetal chromosomal abnormalities (fetal aneuploidy) or ultrasound findings
# of a suspected chromosomal abnormality (excluding soft markers as only
# ultrasound findings)
# •
# Early onset FGR (<32 weeks)<12 weeks may be a sign of fetal aneuploidy 11,12
# """

# # Define the regular expression pattern
# pattern = r'<\d+ weeks'

# # Find all matches in the text
# matches = re.findall(pattern, text)

# # Print the matches

# if any(matches):
#     months = []
#     for match in matches:
#         months.append(int(match.split(" ")[0][1:]))
# months.sort()
# print(months[-1])

# import re

# text = """
# Key Analysis:
# - Fetal presentation should be assessed by abdominal palpation (Leopold's) at 36 weeks or later, when presentation is likely to influence the plans for the birth.
# - Suspected fetal malpresentation should be confirmed by an ultrasound assessment.
# - An ultrasound can be performed at ≥36 weeks gestation to determine fetal position to allow for external cephalic version.
# - Ultrasound to determine fetal position is not necessary prior to 36 weeks gestation unless delivery is imminent.

# Recommendation:
# - To confirm suspected abnormal fetal position or presentation (transverse or breech presentation) at ≥36 weeks gestation, report one of the following:
# - CPT® 76805 (plus CPT® 76810 for each additional fetus) when complete anatomy scan has not yet been performed in the pregnancy
# - CPT® 76815 for limited ultrasound to check fetal position
# - CPT® 76816 if version is being considered and/or for delivery planning
# - CPT® 76815 should never be reported with complete studies CPT® 76801/CPT® 76802, CPT® 76805/CPT® 76810, or CPT® 76811/CPT® 76812 or with CPT® 76816 or BPP (CPT® 76818 and CPT® 76819).
# """

# # Define the regular expression pattern to capture data after "Recommendation:"
# pattern = r'Recommendation:(.*)'

# # Find the match
# match = re.search(pattern, text, re.DOTALL)
# # text_without_recommendation = re.sub(pattern, 'No data found', text, flags=re.DOTALL) # to replace recommendation with new

# # Extract and print the data after "Recommendation:"
# if match:
#     recommendation_data = match.group(1).strip()
#     print(recommendation_data)

# import re

# text = """
# Key Analysis:
# - Fetal presentation should be assessed by abdominal palpation (Leopold's) at 36 weeks or later, when presentation is likely to influence the plans for the birth.
# - Suspected fetal malpresentation should be confirmed by an ultrasound assessment.
# - An ultrasound can be performed at ≥36 weeks gestation to determine fetal position to allow for external cephalic version.
# - Ultrasound to determine fetal position is not necessary prior to 36 weeks gestation unless delivery is imminent.

# Recommendation:
# - To confirm suspected abnormal fetal position or presentation (transverse or breech presentation) at ≥36 weeks gestation, report one of the following:
# - CPT® 76805 (plus CPT® 76810 for each additional fetus) when complete anatomy scan has not yet been performed in the pregnancy
# - CPT® 76815 for limited ultrasound to check fetal position
# - CPT® 76816 if version is being considered and/or for delivery planning
# - CPT® 76815 should never be reported with complete studies CPT® 76801/CPT® 76802, CPT® 76805/CPT® 76810, or CPT® 76811/CPT® 76812 or with CPT® 76816 or BPP (CPT® 76818 and CPT® 76819).
# """

# # Define the regular expression pattern to capture the "Recommendation:" section
# pattern = r'Recommendation:(.*)'

# # Replace the "Recommendation" section with "No data found"
# text_without_recommendation = re.sub(pattern, 'Recommendation:\nNo data found', text, flags=re.DOTALL)

# print(text_without_recommendation)
# from sentence_transformers import SentenceTransformer

# from chromadb import Chroma
# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('all-MiniLM-L6-v2')

# strings = ["string1", "string2", "string3"]
# embeddings = model.encode(strings)

# chroma_db = Chroma(persist_directory='./chroma_db')

# for i, embedding in enumerate(embeddings):
#    chroma_db.add_embedding(embedding, id=i)

# chroma_db.save()

# chroma_db.load()

# query_embedding = model.encode(["query_string"])
# most_similar_ids = chroma_db.get_most_similar(query_embedding, top_k=1)

# print(most_similar_ids)

from create_pdf_list import ele1, ele2, ele3, ele4, ele5, ele6, ele7, ele8, ele9, ele10, ele11, ele12, ele13, ele14, ele15, ele16, ele17, ele18, ele19, ele20, ele21, ele22, ele23, ele24, ele25, ele26, ele27, ele28, ele29, ele30, ele31, ele32, ele33, ele34, ele35, ele36, ele37, ele38, ele39, ele40, ele41, ele42, ele43, ele44, ele45, ele46, ele47, ele48, ele49, ele50, ele51, ele52, ele53, ele54, ele55, ele56, ele57, ele58, ele59, ele60, ele61, ele62, ele63, ele64, ele65, ele66, ele67, ele68, ele69, ele70, ele71, ele72, ele73, ele74, ele75, ele76, ele77, ele78, ele79, ele80, ele81, ele82, ele83, ele84
import chromadb
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key="YOUR_API_KEY",
                model_name="text-embedding-ada-002"
            )
client = chromadb.PersistentClient(path="./db_chroma")
# collection = client.create_collection(name="my_collection", embedding_function=openai_ef)
# collection = client.get_collection(name="my_collection", embedding_function=openai_ef)

# collection = client.get_collection(name="test") # Get a collection object from an existing collection, by name. Will raise an exception if it's not found.
collection = client.get_or_create_collection(name="test") # Get a collection object from an existing collection, by name. If it doesn't exist, create it.
# client.delete_collection(name="my_collection") # Delete a collection and all associated embeddings, documents, and metadata. ⚠️ This is destructive and not reversible

collection.add(
            documents=[str(ele1), str(ele2), str(ele3), str(ele4), str(ele5), str(ele6), str(ele7), str(ele8), str(ele9), str(ele10), str(ele11), str(ele12), str(ele13), str(ele14), str(ele15), str(ele16), str(ele17), str(ele18), str(ele19), str(ele20), str(ele21), str(ele22), str(ele23), str(ele24), str(ele25), str(ele26), str(ele27), str(ele28), str(ele29), str(ele30), str(ele31), str(ele32), str(ele33), str(ele34), str(ele35), str(ele36), str(ele37), str(ele38), str(ele39), str(ele40), str(ele41), str(ele42), str(ele43), str(ele44), str(ele45), str(ele46), str(ele47), str(ele48), str(ele49), str(ele50), str(ele51), str(ele52), str(ele53), str(ele54), str(ele55), str(ele56), str(ele57), str(ele58), str(ele59), str(ele60), str(ele61), str(ele62), str(ele63), str(ele64), str(ele65), str(ele66), str(ele67), str(ele68), str(ele69), str(ele70), str(ele71), str(ele72), str(ele73), str(ele74), str(ele75), str(ele76), str(ele77), str(ele78), str(ele79), str(ele80), str(ele81), str(ele82), str(ele83), str(ele84)], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
            metadatas=[{"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}, {"source": "Admin"}], # filter on these!
            ids=["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q27", "q28", "q29", "q30", "q31", "q32", "q33", "q34", "q35", "q36", "q37", "q38", "q39", "q40", "q41", "q42", "q43", "q44", "q45", "q46", "q47", "q48", "q49", "q50", "q51", "q52", "q53", "q54", "q55", "q56", "q57", "q58", "q59", "q60", "q61", "q62", "q63", "q64", "q65", "q66", "q67", "q68", "q69", "q70", "q71", "q72", "q73", "q74", "q75", "q76", "q77", "q78", "q79", "q80", "q81", "q82", "q83", "q84"], # unique for each doc
         )

