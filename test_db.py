from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import json

query = "placenta previa"
persist_directory = './db'
embedding = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
docs = vectordb.similarity_search(query,k=2,search_type="similarity")
print(docs)
