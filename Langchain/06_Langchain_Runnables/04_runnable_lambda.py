# Runnable lambda can run functions as chains

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnablePassthrough, RunnableLambda

load_dotenv()

def word_count(text):
    return len(text.split())

model = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')
parser = StrOutputParser()

prompt1 = PromptTemplate(
    template = "Generate a joke about {topic}",
    input_variables=['topic']
)

joke_generator_chain = RunnableSequence(prompt1, model, parser)

parallel_chain = RunnableParallel({
    'joke': RunnablePassthrough(),
    'word_count': RunnableLambda(word_count)
    # 'word_count': RunnableLambda(lambda x:len(x.split()))     # works the same
})

final_chain = RunnableSequence(joke_generator_chain, parallel_chain)

result = final_chain.invoke({'topic': 'books'})

final_result = """{} \n word count - {}""".format(result['joke'], result['word_count'])
print(final_result)