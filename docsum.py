import os
import argparse
import fulltext
import re
import time
from groq import Groq

def split_document_into_chunks(text):
    r"""
    Split the input text into a list of paragraphs so that an LLM can process those
    paragraphs individually.

    Arguments:
        text (str): The original document to split up.
    
    Returns:
        split_text (list): The document as a series of strings in a list.
        
    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.')
    ['This is a paragraph.', 'This is another paragraph.']
    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.\n\nThis is yet another paragraph.')
    ['This is a paragraph.', 'This is another paragraph.', 'This is yet another paragraph.']
    >>> split_document_into_chunks('This is a paragraph.')
    ['This is a paragraph.']
    >>> split_document_into_chunks('')
    []
    >>> split_document_into_chunks('This is a paragraph.\n')
    ['This is a paragraph.']
    >>> split_document_into_chunks('This is a paragraph.\n\n')
    ['This is a paragraph.']
    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.\n\n')
    ['This is a paragraph.', 'This is another paragraph.']
    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.\n\nThis is yet another paragraph.\n\n')
    ['This is a paragraph.', 'This is another paragraph.', 'This is yet another paragraph.']
    """
    if not text:
        return []

    # Split the document by two or more newlines
    paragraphs = re.split(r'\n{2,}', text)
    
    # Remove leading/trailing newlines and spaces from each paragraph
    cleaned_paragraphs = [para.strip() for para in paragraphs if para.strip()]
    
    return cleaned_paragraphs

def rate_limited_request(client, request_function, *args, **kwargs):
    """
    Wrapper function to ensure requests are rate-limited.
    """
    last_request_time = time.time()
    request_interval = 60 / 30  # 60 seconds / 30 requests per minute

    # Wait if necessary to stay within rate limit
    elapsed_time = time.time() - last_request_time
    if elapsed_time < request_interval:
        time.sleep(request_interval - elapsed_time)

    # Update the time of the last request
    last_request_time = time.time()
    
    return request_function(*args, **kwargs)

if __name__ == '__main__':
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    parser = argparse.ArgumentParser(description='Summarizes a document with groq.')
    parser.add_argument('filename', help='Provide the path to a document to summarize.')
    args = parser.parse_args()

    # Get the full text from the document
    try:
        with open(args.filename, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        text = fulltext.get(args.filename)

    print("\n")
    print(f"Summarizing {args.filename}")
    print("\n")
    print(f"DEBUG: length of text: {len(text)}")
    print("\n")
    print("\n")
    print(f"DEBUG: text: {text}")
    print("\n")
    print("\n")

    try:
        response = rate_limited_request(
            client.chat.completions.create,
            messages=[{
                        "role": "system",
                        "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.",
                    },
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
            model="llama3-8b-8192"
        )
    except:
        # Split the document into chunks
        chunked_text = split_document_into_chunks(text)
        print(f"DEBUG: length of chunked_text: {len(chunked_text)}")

        # Initialize an empty list for storing individual summaries
        summarized_chunks = []

        # Summarize each paragraph
        for i, chunk in enumerate(chunked_text):
            print(f"DEBUG: chunk {i}")
            print(f"DEBUG: length of chunk: {len(chunk)}")
            print(f"DEBUG: chunk: {chunk}")
            chat_completion = rate_limited_request(
                client.chat.completions.create,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.",
                    },
                    {
                        "role": "user",
                        "content": chunk,
                    }
                ],
                model="llama3-8b-8192"
            )
            summarized_chunks.append(chat_completion.choices[0].message.content)

        # Concatenate all summarized paragraphs into a smaller document
        summarized_document = " ".join(summarized_chunks)

        # Summarize the entire document again
        response = rate_limited_request(
            client.chat.completions.create,
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.",
                },
                {
                    "role": "user",
                    "content": summarized_document,
                }
            ],
            model="llama3-8b-8192"
        )

    # Output summary
    print(response.choices[0].message.content)
