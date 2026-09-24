#LCEL - Langchain Expression Language makes things easier and provides Quality of life features such as replacing "RunnableSequence(chain1, chain2)" syntax with simple "chain1 | chain2" syntax

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
model = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')

prompt1 = PromptTemplate(
    template = "Generate a short tweet about {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template = "Generate a small linkedin post on {topic}",
    input_variables=['topic']
)

parser = StrOutputParser()

#replacing RunnableParallel with a simple dictionary also works the same thanks to LCEL
parallel_chain = {                      #RunnableParallel
    'tweet': prompt1 | model | parser,  #RunnableSequence
    'linkedin': prompt2 | model | parser
}

result = parallel_chain.invoke({'topic': 'AI'})
print(result)