import os
import argparse
import fulltext
import re
import groq
from bs4 import BeautifulSoup
import chardet
import time

def import_doc(filename):
    # Get the full text from the document
    with open(filename, 'rb') as f:
        result = chardet.detect(f.read())
        utf = result['encoding']
        print(f"DEBUG: encoding: {utf}")

    if filename.endswith('.html'):
        print("DEBUG: file ends with html, using BeautifulSoup")
        with open(args.filename, 'r', encoding=utf) as f:
            soup = BeautifulSoup(f, 'html.parser')
            text = soup.get_text()
    else:
        try:
            print("DEBUG: trying open()")
            with open(args.filename, 'r', encoding=utf) as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"DEBUG: open didn't work, trying fulltext")
            text = fulltext.get(args.filename)

    print(f"DEBUG: length of text: {len(text)}")

    return text

def split_document_into_chunks(text, max_chunk_size=4000):
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

    chunks = []
    current_chunk = ""
    
    for para in cleaned_paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chunk_size:  # +2 for potential newlines
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n"  # Add a separator between paragraphs
            current_chunk += para
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def groq_query(input_text, delay=5):
    """
    
    
    Arguments:
    
    Returns:
    """
    try:
        final_chat = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.",
                },
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model="llama3-8b-8192",
        )

    except groq.InternalServerError:
        print("DEBUG: groq broke let's try again")
        time.sleep(delay)
        final_chat = groq_query(input_text)

    except (groq.RateLimitError, groq.BadRequestError) as e:
        
        error_message = str(e)

        if 'RMP' in error_message:
            print(f"DEBUG: too much too quickly, waiting {delay} seconds")
            time.sleep(delay)
            final_chat = groq_query(input_text)
        else:
            # Split the document into chunks
            chunked_text = split_document_into_chunks(input_text)
            print("\n")
            print(f"DEBUG: number of chunks: {len(chunked_text)}")
            print("\n")

            # Initialize an empty list for storing individual summaries
            summarized_chunks = []

            # Summarize each paragraph
            for i, chunk in enumerate(chunked_text):
                print(f"DEBUG: chunk {i}")
                print(f"DEBUG: length of chunk: {len(chunk)}")
                print(f"DEBUG: chunk: {chunk}")
                print("\n")
                chunk_chat = groq_query(chunk)
                chunk_txt = chunk_chat.choices[0].message.content
                print(f"DEBUG: internal response: {chunk_txt}")
                print("\n")
                summarized_chunks.append(chunk_txt)

            # Concatenate all summarized paragraphs into a smaller document
            summarized_document = " ".join(summarized_chunks)
            print("\n")
            print(f"DEBUG: length of summarized document: {len(summarized_document)}")
            print(f"DEBUG: summarized_document: {summarized_document}")
            print("\n")
            
            final_chat = groq_query(summarized_document)

    return final_chat

if __name__ == '__main__':
    client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

    parser = argparse.ArgumentParser(description='Summarizes a document with groq.')
    parser.add_argument('filename', help='Provide the path to a document to summarize.')
    args = parser.parse_args()

    print(f"DEBUG: summarizing {args.filename}")

    text = import_doc(args.filename)

    summary_chat = groq_query(text)
    summary_txt = summary_chat.choices[0].message.content

    # Output summary
    print("\n")
    print("DEBUG: final response:")
    print(summary_txt)
    print("\n")
