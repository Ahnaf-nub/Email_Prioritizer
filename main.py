from dotenv import load_dotenv
load_dotenv()
import os
from nylas import Client
import google.generativeai as genai
from langchain import PromptTemplate, LLMChain

grant_id = os.environ.get('NYLAS_GRANT_ID')
GOOGLE_API_KEY = os.getenv('API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

gemini = genai.GenerativeModel('gemini-1.5-flash')

template = """
Analyze the following email content:
Sender: {sender}
Subject: {subject}
Content: {content}
Determine the urgency and importance of this email.
"""

llm_chain = LLMChain(llm=gemini, prompt_template=PromptTemplate(template=template))

# Initialize your Nylas API client
nylas = Client(
    os.environ.get('NYLAS_API_KEY'),
    os.environ.get('NYLAS_API_URI')
)
emails = messages = nylas.messages.list(
  grant_id,
  query_params={
    "limit": 10
  }
)

# Retrieve Application Information
application = nylas.applications.info()
application_id = application[1]
print("Application ID:", application_id)   

prioritized_emails = []

for email in emails:
    context = {
        "sender": email['from'],
        "subject": email['subject'],
        "content": email['body']
    }
    response = llm_chain.run(context)
    prioritized_emails.append((email, response))

# Sort emails based on the LLM's analysis
prioritized_emails.sort(key=lambda x: x[1]['priority_score'], reverse=True)
