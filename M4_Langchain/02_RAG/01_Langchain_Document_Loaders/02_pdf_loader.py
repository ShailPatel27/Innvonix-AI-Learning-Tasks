# loads pdf
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('./Langchain/07_Langchain_Document_Loaders/02_dl-curriculum.pdf')

docs = loader.load()

print(docs)

print("Number of pages: ", len(docs))

print(docs[0].page_content)
print(docs[1].metadata)