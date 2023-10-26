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