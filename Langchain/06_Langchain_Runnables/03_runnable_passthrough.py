# you cant normally pass the input as it is in the output with langchain. so runnable passthrough is used for that purpose.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnablePassthrough

load_dotenv()
model = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')
parser = StrOutputParser()

passthrough = RunnablePassthrough()

prompt1 = PromptTemplate(
    template = "Generate a joke about {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template = "Explain the following joke in short: \n {joke}",
    input_variables=['joke']
)

joke_generator_chain = RunnableSequence(prompt1, model, parser)

parallel_chain = RunnableParallel({
    'joke': RunnablePassthrough(),
    'explaination': RunnableSequence(prompt1, model, parser)
})

final_chain = RunnableSequence(joke_generator_chain, parallel_chain)

print(final_chain.invoke({'topic': 'AI'}))