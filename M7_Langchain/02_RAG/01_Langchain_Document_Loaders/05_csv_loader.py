from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(file_path='./Langchain/07_Langchain_Document_Loaders/05_Social_Network_Ads.csv')

docs = loader.load()
print(docs[0])      # for every row you get 1 document object