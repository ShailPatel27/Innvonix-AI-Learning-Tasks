from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# chat template
chat_template = ChatPromptTemplate([
    ('system', 'You are a helpful customer support agent'),
    MessagesPlaceholder(variable_name='chat_history'),  # to retrieve and store chat history
    ('human', '{query}')
])

# chat history
chat_history = []
with open ('./Langchain_Prompts/chat_history.txt') as f:
    chat_history.extend(f.readlines())

print(chat_history)

# create prompt
prompt = chat_template.invoke({'chat_history': chat_history, 'query': 'Where is my refund'})

print(prompt)