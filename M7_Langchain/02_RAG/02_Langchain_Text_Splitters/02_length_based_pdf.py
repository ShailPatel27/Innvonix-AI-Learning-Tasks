from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('./Langchain/08_Langchain_Text_Splitters/02_dl-curriculum.pdf')
docs = loader.load()

splitter = CharacterTextSplitter(
    chunk_size=100,     # max number of characters in a chunk
    chunk_overlap=0,    # number of characters that repeat in 2 chunks ([chunk-1: [ABCD{EF]GHIJ} : chunk-2). here overlap is 2 and EF repeat for both chunk 1 and 2
    separator=''
)

result = splitter.split_documents(docs)
print(result[0])    # first chunk of 100 characters