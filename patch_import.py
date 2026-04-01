import re

with open('tailor.py', 'r') as f:
    content = f.read()

content = content.replace("from langchain_classic.chains import RetrievalQA", "from langchain.chains import RetrievalQA")

with open('tailor.py', 'w') as f:
    f.write(content)
