import os
import argparse
import fulltext
from groq import Groq

def split_document_into_chunks(text):
    r"""      
    Split the input text into smaller chunks so that an LLM can process those
    chunks individual.      
        
    Arguments:          
        text (str): The original document to split up.     
        
    Returns:    
        xxx (list): The document as a series of strings in a list.             
        
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.')
    ['This is a sentence.', 'This is another paragraph.']
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.\n\nThis is yet another paragraph.')
    ['This is a sentence.', 'This is another paragraph.', 'This is yet another paragraph.']
    >>> split_document_into_chunks('This is a sentence.')
    ['This is a sentence.']
    >>> split_document_into_chunks('')
    []
    >>> split_document_into_chunks('This is a sentence.\n')
    ['This is a sentence.']
    >>> split_document_into_chunks('This is a sentence.\n\n')
    []
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.\n\n')
    ['This is a sentence.', 'This is another paragraph.']
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.\n\nThis is yet another paragraph.\n\n')
    ['This is a sentence.', 'This is another paragraph.', 'This is yet another paragraph.']
    """
    return text.split('\n\n')

# TODO: edit split function to pass doctests
# TODO: call the split document into chunks on text
# TODO: for each paragraph in the output list call the LLM code below to
# summarize it
# TODO: put the summary into a new list
# TODO: concatenate that new list into one smaller document
# TODO; recall that the LLM code below on the new smaller document

if __name__ == '__main__':
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    parser = argparse.ArgumentParser(description='Summarizes a document with groq.')
    parser.add_argument('filename', help='Provide the path to a document to summarize.')
    args = parser.parse_args()
    
    # TODO: change the text variable to avoid redefining
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
