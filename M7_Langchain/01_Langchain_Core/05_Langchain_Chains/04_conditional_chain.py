from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
import os

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()

class Feedback(BaseModel):
    sentiment: Literal['positive', 'negative'] = Field(description='Give the sentiment of the feedback')


parser2 = PydanticOutputParser(pydantic_object=Feedback)

prompt1 = PromptTemplate(
    template="Classify the sentinment of the following feedback text into positive or negative: \n {feedback} \n {format_instruction}",
    input_variables=['feedback'],
    partial_variables={'format_instruction': parser2.get_format_instructions()}
)

classifier_chain = prompt1 | model | parser2
# classifier_chain = {
#     "sentiment": prompt1 | model | parser2,
#     "feedback": RunnablePassthrough() 
# }

prompt2 = PromptTemplate(
    template = 'Write an explicit, direct customer response to this specific positive feedback. Do not provide a list of options or placeholders: \n {feedback}',
    input_variables = ['feedback']
)

prompt3 = PromptTemplate(
    template = 'Write an explicit, direct customer response to this specific negative feedback. Do not provide a list of options or placeholders: \n {feedback}',
    input_variables = ['feedback']
)

# branch_chain = RunnableBranch(      #like switch case
#     (condition_1, chain_1),
#     (condition_2, chain_2),
#           ...
#     (condition_n, chain_n),
#     default chain
# )

branch_chain = RunnableBranch(
    (lambda x: x['sentiment'].sentiment == 'positive', prompt2 | model | parser),
    (lambda x: x['sentiment'].sentiment == 'negative', prompt3 | model | parser),
    RunnableLambda(lambda x: "could not find sentiment")
)

chain = (
    {
        "sentiment": classifier_chain, 
        "feedback": lambda x: x["feedback"]  # Passes the string directly down to prompt2/prompt3
    } | branch_chain
)

print(chain.invoke({'feedback': 'this is a terrible phone'}))

chain.get_graph().print_ascii()