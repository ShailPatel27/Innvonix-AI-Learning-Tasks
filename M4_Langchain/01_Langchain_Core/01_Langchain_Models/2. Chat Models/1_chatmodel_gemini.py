from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite', temperature=1.5, max_completion_tokens=10)

result = model.invoke("Whats 2+2")

print(result.text)