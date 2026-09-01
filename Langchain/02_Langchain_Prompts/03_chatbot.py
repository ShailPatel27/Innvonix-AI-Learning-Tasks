from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.7-flash')

chat_history = [
    SystemMessage(content='You are a helpful AI assistant who responds in under 10 words')
]

while True:
    user_input = input('You: ')
    
    chat_history.append(HumanMessage(content=user_input))
    
    if user_input == 'exit':
        break
    result = model.invoke(chat_history)
    
    chat_history.append(AIMessage(content=result.text))
    
    print("AI: ", result.text)

print(chat_history)