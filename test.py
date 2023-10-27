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


import difflib
import re

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

from flask import Flask, render_template, request, Response
import openai
from flask import jsonify
import os
import openai
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from pdf_utils import PDFUtils

from insights import insightsAll

# abnormalities = {'Fetal Position': 'Breech', 'Known Macrosomia ≥90th percentile': 'EFW is 76.87 pctl', 'Breech presentation': 'yes', 'Mild pyelectasis': '', 'right kidney': 'unseen', 'Suboptimal cardiac views': '', 'Unable to obtain optimal ACI and spine views': '', 'Short and closed cervix': ''}

def get_completion(prompt, model="gpt-3.5-turbo"):
    # messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=0.4  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

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


