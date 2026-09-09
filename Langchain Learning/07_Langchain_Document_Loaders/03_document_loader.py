# loads entire directory which may contain multiple pdfs
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

loader = DirectoryLoader(
    path='./Langchain/07_Langchain_Document_Loaders/03_papers',
    glob='*.pdf',   #pattern to select specific files
    loader_cls=PyPDFLoader  #loader to load things from the directory
)

docs = loader.lazy_load()   #loads document on demand, then clears memory for the next document and so on.

print(type(docs))
for document in docs:
    print(document.metadata)
    