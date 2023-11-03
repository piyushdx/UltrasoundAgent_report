from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
load_dotenv()
from langchain.prompts import PromptTemplate
import openai
import re


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
    def __init__(self, pdf_folder_path, persist_directory):
        self.pdf_folder_path = pdf_folder_path
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()
        self.vectordb = None
        self.retriever = None
        self.qa_chain = None

    def create_vector_db_from_pdfs(self):
        loader = PyPDFDirectoryLoader(self.pdf_folder_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        embedding = OpenAIEmbeddings()
        self.vectordb = Chroma.from_documents(
            documents=texts, embedding=embedding, persist_directory=self.persist_directory)
        self.vectordb.persist()

        print("db is created.")

    def initialize_qa_chain(self):
        self.embedding = OpenAIEmbeddings()
        self.vectordb = Chroma(
            persist_directory=self.persist_directory, embedding_function=self.embedding)
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 2})
        self.qa_chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(
            temperature=0.2), retriever=self.retriever, return_source_documents=True)

    def process_llm_response(self, llm_response):
        print("Bot  : " + llm_response['answer'])
        print('\nSources:')
        for source in llm_response["source_documents"]:
            print("     " + source.metadata['source'] +
                  " page: " + str(source.metadata['page']))
        print('\n')

    def chat_with_pdf(self):
        chat_history = []
        print("Bot  : How can I help you?")
        while True:
            query = input('User : ')
            result = self.qa_chain(
                {"question": query, 'chat_history': chat_history}, return_only_outputs=False)
            chat_history += [(query, result["answer"])]
            self.process_llm_response(result)

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
    
    def chat_with_pdf_q(self,db, query,AUA,query_context):
        print(query)
        if "Socio-Demographic Risk Factors (maternal age)" in query:
            final_ans = ans_for_age
        elif "myoma" in str.lower(query):
            final_ans = ans_for_myoma
        else :
            prompt_template = """ Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.
            [STRICT RULES TO FOLLOW WHILE GIVING ANSWER]
                1.do not infer or generate your own answers. Answer questions based solely on provided context. 
                2.If you cannot locate the answer within the given <Context>, simply state, "The answer is not found in the provided context."
                3.If the key analysis suggests that the condition is considered normal, commonly encountered,common finding or benign, your response should strictly say and only say following in Recommendation... Recommendation: "No Recommendation Needed Cause Findind is Normal"

            [Sample Question]
                I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
            [Sample Output] 
                Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
                    actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
                    Circumference ≤10th percentile.
                Recommendation:
                    • Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
                    • Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
                    can be performed once or twice weekly
                    • Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
                    weekly
                    • Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
                    performed every 2 to 4 weeks if complete anatomy ultrasound previously performed

            [Context]
            
            <context>
            """

            results = db.get_context(que=query_context)
            context,page = db.get_context_combined(results)

            history = [{"role": "system", "content": prompt_template.replace("<context>",context)},{"role": "user", "content": f"{query}" }]
            final_ans = get_completion(history)
            print(f"page number is {page}")
            final_ans += "\nPage : "+str(page)

            contain_cpt_reports = contains_cpt_code(final_ans)
            print(f"contain cpt reports : {contain_cpt_reports}")
            if not contain_cpt_reports:
                final_ans = " "


        try:
            if len(final_ans.split("Recommendation:")[1].strip())<110:
                if "The answer is not found in the provided context." in final_ans or "No Recommendation Needed Cause Finding is Normal" in final_ans:
                    final_ans = " "
                    AUA = None
        except Exception as e:
            pass

        text_list = find_and_extract_abnormalities(str.lower(final_ans))
        changes = find_changes_in_first_word(text_list)
        # print("\nBelow are the list of change:")
        # print(changes)
        
        for change in changes:
            prompt_known_suspected = [{"role": "system", "content": f"""In the given report remove all points related to suspected {change} and keep points related to known {change} and everything else."""},{"role":"user", "content": """The ultrasound report is as follows:""" + "\n" + final_ans}]
            final_ans = get_completion(prompt_known_suspected)

# "You are an expert in filtering Ultrasound reports. You get the ultrasound report draft and you create the final version. Your role is to remove unwanted recommendations Based on fetus age in weeks. The rule of thumb is to only include recommendations that are applicable as of now or in future. You should remove all the recommendations which should have been done in the past according to the current fetal age. The fetal age will be given to you. Take a deep breath and work your magic to filter the ultrasound reports."
        AUA = None
        if AUA is not None:

            pattern = r'Recommendation:(.*)'

            # Find the match
            match = re.search(pattern, final_ans, re.DOTALL)

            # Extract and print the data after "Recommendation:"
            if match:
                recommendation_data = match.group(1).strip()

            pattern = r'<\d+ weeks'
            
            print("below is recommendation data....")
            print(recommendation_data)

            # Find all matches in the text
            matches = re.findall(pattern, recommendation_data)

            # Print the matches

            if any(matches):
                months = []
                for match in matches:
                    months.append(int(match.split(" ")[0][1:]))
            months.sort()
            print(months)
            # print(months[-1])


            # prompt_filter_fetus_age = [{"role": "system", "content":filter_by_AUA_prompt},
            #         {"role":"user", "content": f"""The fetal age is {AUA} weeks. The ultrasound report is as follows:""" + "\n" + final_ans}]

            # final_ans = get_completion(prompt_filter_fetus_age)

            filter_by_AUA_prompt = f"""
            show all the remaining information after eliminate recommendations intended to do CPT report <{str(months[-1])} weeks.
            """
            prompt_filter_fetus_age = [{"role": "system", "content":filter_by_AUA_prompt},{"role":"user", "content": f"""The ultrasound report is as follows:""" + "\n" + final_ans}]
            new_recommendations = get_completion(prompt_filter_fetus_age)    
            print(new_recommendations)


            final_ans = re.sub(pattern, "Recommendation:\n"+new_recommendations, final_ans, flags=re.DOTALL) # to replace recommendation with new

            print("below is final answer")
            print(final_ans)
            print("-------------------")
            # text_list = find_and_extract_abnormalities(str.lower(final_ans))
            # changes = find_changes_in_first_word(text_list)
            # # print("\nBelow are the list of change:")
            # # print(changes)
            
            # for change in changes:
            #     prompt_known_suspected = [{"role": "system", "content": f"""In the given report remove all points related to suspected {change} and keep points related to known {change} and everything else."""},{"role":"user", "content": """The ultrasound report is as follows:""" + "\n" + final_ans}]
            #     final_ans = get_completion(prompt_known_suspected)
            



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
