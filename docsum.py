import os
import argparse
import fulltext
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

parser = argparse.ArgumentParser(description='Summarizes a document with groq.')
parser.add_argument('filename', help='Provide the path to a document to summarize.')
args = parser.parse_args()

text = fulltext.get(args.filename)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade readling level.",
        },
        {
            "role": "user",
            "content": text,
        }
    ],
    model="llama3-8b-8192",
)
print(chat_completion.choices[0].message.content)
