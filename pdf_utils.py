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
        # self.qa_chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(
        #     temperature=0.2), retriever=self.retriever, return_source_documents=True)

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

    def chat_with_pdf_q(self, query):

        prompt_template = """ Please adhere closely to the provided <output sample> and ensure that your response should be concise with Structured bullet point.
        [Output sample]
            Key Analysis: 
            Recommendation: 
        
        For Example : 
        Question: I would like comprehensive guidelines for the AC value 8% along with CPT reports.\n"
        Output : 
            Key Analysis: AC &lt; 10%, The ACOG definition of Fetal Growth Restriction (FGR): Estimated or
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
        print(final_ans)
        return final_ans


# Use When you want to create a db
# pdf_folder_path = "ChatBotUI/static/pdf"
# persist_directory = "./db"

# # Create an instance of PDFUtils class
# pdf_utils = PDFUtils(pdf_folder_path, persist_directory)

# # Call the initialize_qa_chain method to initialize the QA chain
# pdf_utils.create_vector_db_from_pdfs()
