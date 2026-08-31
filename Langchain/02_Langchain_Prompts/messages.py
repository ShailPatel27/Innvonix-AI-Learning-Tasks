from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

messages = [
    SystemMessage(content='You are a helpful assistant who gives answers in under 10 words'),
    HumanMessage(content='Tell me about Langchain')
]

result = model.invoke(messages)

messages.append(AIMessage(content=result.text))
print(messages)