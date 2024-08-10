from dotenv import load_dotenv
load_dotenv()
import os
import warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
from nylas import Client
from langchain import PromptTemplate, LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

grant_id = os.environ.get('NYLAS_GRANT_ID')
gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

template = """
Analyze the following email content:
Subject: {subject}
Content: {content}
Determine the urgency and importance of this email.
"""
def body2txt(body):
    soup = BeautifulSoup(body)
    return soup.get_text('\n')


def get_subject_from_id(msg_id):
    #print(msg_id)
    message = nylas.messages.get(f"{msg_id}")
    return message.subject

def get_body_from_id(msg_id):
    #print(msg_id)
    message = nylas.messages.get(f"{msg_id}")
    return body2txt(message.body)

llm_chain = LLMChain(prompt=PromptTemplate(template=template), llm=gemini)

# Initialize your Nylas API client
nylas = Client(
    os.environ.get('NYLAS_API_KEY'),
    os.environ.get('NYLAS_API_URI')
)
emails = nylas.messages.list(
    grant_id,
    query_params={
        "limit": 1,
    }
)

prioritized_emails = []


for email in emails:
  print(get_subject_from_id('1913c1cca8bbe34c'))
  context = {
    "subject": email["subject"],
    "content": body2txt(str(email))
  }
  response = llm_chain.run(context)
  prioritized_emails.append((email, response))

prioritized_emails.sort(key=lambda x: x[1]['priority_score'], reverse=True)

for email, priority in prioritized_emails:
    print(f"Subject: {email['subject']}, Priority: {priority}")
