from dotenv import load_dotenv
load_dotenv()
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

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
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        embedding = OpenAIEmbeddings()
        self.vectordb = Chroma.from_documents(documents=texts, embedding=embedding, persist_directory=self.persist_directory)
        self.vectordb.persist()
        
        print("db is created.")

    def initialize_qa_chain(self):
        self.embedding = OpenAIEmbeddings()
        self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding)
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 2})
        self.qa_chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.2), retriever=self.retriever, return_source_documents=True)

    def process_llm_response(self, llm_response):
        print("Bot  : " + llm_response['answer'])
        print('\nSources:')
        for source in llm_response["source_documents"]:
            print("     " + source.metadata['source'] + " page: " + str(source.metadata['page']))
        print('\n')

    def chat_with_pdf(self):
        chat_history = []
        print("Bot  : How can I help you?")
        while True:
            query = input('User : ')
            result = self.qa_chain({"question": query, 'chat_history': chat_history}, return_only_outputs=False)
            chat_history += [(query, result["answer"])]
            self.process_llm_response(result)

    def chat_with_pdf_q(self, query):
        reply = ""
        qa_chain_result = self.qa_chain({"question": query, 'chat_history': []}, return_only_outputs=False)
        reply += qa_chain_result["answer"]
        reply += '\nSource Pages : '
        page_set = set()
        for source in qa_chain_result["source_documents"]:
            page_set.add(source.metadata['page']+1) # GPT given pages are always currunt page - 1
        return reply+str(list(page_set))

## Use When you want to create a db
# pdf_folder_path = "ChatBotUI/static/pdf"
# persist_directory = "./db"

# # Create an instance of PDFUtils class
# pdf_utils = PDFUtils(pdf_folder_path, persist_directory)

# # Call the initialize_qa_chain method to initialize the QA chain
# pdf_utils.create_vector_db_from_pdfs()