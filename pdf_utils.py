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
    
    def chat_with_pdf_q(self, query,AUA):

        prompt_template = """ Please adhere closely to the provided <Sample Output> and ensure that your response should be concise with Structured bullet point.
        [Sample Output]
            Key Analysis: //will solely consist of an explanation of the analysis. 
            Recommendation: //will include all the CPT reports ang guidelines, just as demonstrated in the <Sample Output>.
        
        [Sample Question]
            I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
        [Sample Output] 
            Key Analysis: AC < 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
                actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
                Circumference ≤10th percentile.
            Recommendation:
                 Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
                 Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
                can be performed once or twice weekly
                 Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
                weekly
                 Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
                performed every 2 to 4 weeks if complete anatomy ultrasound previously performed

        Context : {context}
        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context","question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0.2), retriever=self.retriever, chain_type_kwargs=chain_type_kwargs)

        final_ans = qa.run(query)
        print("\n\nBelow is the Row Answer:\n\n")
        print(final_ans)

        prompt_filter_fetus_age = [{"role": "system", "content": """You are an expert in filtering Ultrasound reports. You get the ultrasound report draft and you create the final version. Your role is to remove unwanted recommendations related to age. The rule of thumb is to only include recommendations that are applicable as of now or in future. You should remove all the recommendations which should have been done in the past according to the current fetal age. The fetal age will be given to you. Take a deep breath and work your magic to filter the ultrasound reports."""},
                {"role":"user", "content": f"""The fetal age is {AUA}. The ultrasound report is as follows:""" + "\n" + final_ans}]

        final_ans = get_completion(prompt_filter_fetus_age)
        
        text_list = find_and_extract_abnormalities(str.lower(final_ans))
        changes = find_changes_in_first_word(text_list)
        print("\nBelow are the list of change:")
        print(changes)
        
        for change in changes:
            prompt_known_suspected = [{"role": "system", "content": f"""In the given report remove all points related to suspected {change} and keep points related to known {change} and everything else."""},{"role":"user", "content": """The ultrasound report is as follows:""" + "\n" + final_ans}]
            final_ans = get_completion(prompt_known_suspected)

        print(final_ans)
        print("\n\n")

        return final_ans

    # def chat_with_pdf_q(self, query):
            
    #         # age = "26 week"
    #         age = 26
    #         if age >= 16:
    #             add_prompt = """Since the patient is <age> weeks pregnant, Recommend the CPT report code for gestational age of >=16 weeks only. Don't recommend the report of gestational age of >=36 weeks.
    #             Context : {context}
    #             Question: {question}""".replace("<age>",str(age))
    #         elif age >= 36:
    #             add_prompt = """Since the patient is <age> weeks pregnant, Recommend the CPT report code for gestational age of >=36 weeks only.
    #             Context : {context}
    #             Question: {question}""".replace("<age>",str(age))
                
            
    #         prompt_template = """ Please adhere closely to the provided <output sample> and ensure that your response should be concise with Structured bullet point.
    #         [Output sample]
    #             Key Analysis: You have to filter those CPT 
    #             Recommendation: You have to filter those CPT 
            
    #         For Example : 
    #         Question: I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
    #         Output : 
    #             Key Analysis: AC &lt; 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
    #                 actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
    #                 Circumference ≤10th percentile.
    #             Recommendation:
    #                 You have to filter those CPT 
    #                  Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
    #                  Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
    #                 can be performed once or twice weekly
    #                  Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
    #                 weekly
    #                  Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
    #                 performed every 2 to 4 weeks if complete anatomy ultrasound previously performed
                    

    #         Context : {context}
    #         Question: {question}
    #         Answer:"""
            
    #         print("prompt_template*-*-*--*--*-*-")
    #         print(prompt_template)

    #         # prompt_template = """ Please adhere closely to the provided <output sample> and ensure that your response should be concise with Structured bullet point.
    #         # [Output sample]
    #         #     Key Analysis: 
    #         #     Recommendation: 
            
    #         # For Example : 
    #         # Question: I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
    #         # Output : 
    #         #     Key Analysis: AC &lt; 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
    #         #         actual weight of the fetus ≤10th percentile for gestational age, and/or Abdominal
    #         #         Circumference ≤10th percentile.
    #         #     Recommendation:
    #         #          Detailed Fetal Anatomic Scan (CPT® 76811) at diagnosis if not already performed
    #         #          Starting at 26 weeks, BPP (CPT® 76818 or CPT® 76819) or a modified BPP (CPT® 76815)
    #         #         can be performed once or twice weekly
    #         #          Starting at 23 weeks Umbilical artery (UA) Doppler (CPT® 76820) can be performed
    #         #         weekly
    #         #          Starting at diagnosis, if ≥16 weeks gestation, follow up ultrasound (CPT® 76816) can be
    #         #         performed every 2 to 4 weeks if complete anatomy ultrasound previously performed

    #         # Context : {context}
    #         # Question: {question}
    #         # Answer:"""
    #         PROMPT = PromptTemplate(
    #             template=prompt_template, input_variables=["context","question"]
    #         )
    #         chain_type_kwargs = {"prompt": PROMPT}
    #         qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0.2), retriever=self.retriever, chain_type_kwargs=chain_type_kwargs)
    #         print("*-*-*-*-*-*-*-*-*--*-*-")
    #         print(qa)
    #         final_ans = qa.run(query)
    #         print(final_ans)
            
    #         PROMPT = PromptTemplate(
    #             template=add_prompt, input_variables=["context","question"]
    #         )
    #         chain_type_kwargs = {"prompt":PROMPT }
    #         qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0.2), retriever=self.retriever, chain_type_kwargs=chain_type_kwargs)
    #         final_ans1 = qa.run(final_ans)
    #         print(final_ans1)

            
            
    #         return final_ans1


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
