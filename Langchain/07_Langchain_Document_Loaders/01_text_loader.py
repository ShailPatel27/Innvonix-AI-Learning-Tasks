from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()
model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')
parser = StrOutputParser()

prompt = PromptTemplate(
    template='Write a summary for the following poem: \n {poem}',
    input_variables=['poem']
)

loader = TextLoader('./Langchain/07_Langchain_Document_Loaders/cricket.txt', encoding='utf-8')

docs = loader.load()

print(type(docs))
print("Page Content: ", docs[0].page_content)
print("Metadata: ", docs[0].metadata)

chain = prompt | model | parser

print(chain.invoke({'poem':docs[0].page_content}))