from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()
model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')
parser = StrOutputParser()

prompt = PromptTemplate(
    template='Answer the following question: \n {question} from the following text: \n {text}',
    input_variables=['question', 'text']
)


url = "https://www.amazon.in/HP-Upgradeable-Response-Office24-am0240tx/dp/B0G3VCGXH6/ref=sr_1_3?crid=35JX12QZHNIX8&dib=eyJ2IjoiMSJ9.yE6pSjnS0lBdjjS4hPUmbnntXjrjHe1o_T8ucBxjl2LvNMEKCQ_LP_hFCbeff8eGvYMq_NRZI5HWFEjIS07TzSFaXQLoLR0vquh1uevzhLFByS7w3oMk5EesbRNw3E57s4IZoAcBDMlkvn0B0IzscNQzImQ7YCryKZ7MFcrHtQRwH7wvHkSMcOseTUKY9eFFIGsuTXFM75qk5dlZujWLBXpFH1pRaPPJa3t2JH64jsc.QKJ7NNlu0muBjCtliesqasUTTjRa1TDzEP_TQ_zJjEM&dib_tag=se&keywords=hp%2Bomen&qid=1788778820&sprefix=hp%2Bom%2Caps%2C298&sr=8-3&th=1"
loader = WebBaseLoader(url)

docs = loader.load()
# print(docs)

chain = prompt | model | parser
print(chain.invoke({'question': 'What is the peak brightness', 'text': docs[0].page_content}))