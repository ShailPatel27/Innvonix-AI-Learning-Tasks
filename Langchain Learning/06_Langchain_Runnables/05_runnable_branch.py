# Runnable lambda can run functions as chains

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableBranch

load_dotenv()
model = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')
parser = StrOutputParser()

def word_count(text):
    return len(text.split())

prompt1 = PromptTemplate(
    template="Write a detailed report on {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template="Summarize the following text: \n{text}",
    input_variables=['text']
)

report_generation_chain = RunnableSequence(prompt1, model, parser)

branch_chain = RunnableBranch(
    (lambda x: len(x.split())>500, RunnableSequence(prompt2, model, parser)),
    #like switch case => if output > 500 words: run this chain
    RunnablePassthrough()
    #default case
)

final_chain = RunnableSequence(report_generation_chain, branch_chain)

print(final_chain.invoke({'topic': 'Iron'}))