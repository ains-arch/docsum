import os
import argparse
import fulltext
import re
from groq import Groq

def split_document_into_chunks(text, max_chunk_size=5000):
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
    print(f"DEBUG: summarizing {args.filename}")
    print("\n")
    print(f"DEBUG: length of text: {len(text)}")
    print("\n")
    print(f"DEBUG: text: {text}")
    print("\n")

    try:
        response = client.chat.completions.create( messages=[ {
                    "role": "system",
                    "content": "Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.",
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
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
            chat_completion = client.chat.completions.create(
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
                model="llama3-8b-8192",
            )
            summarized_chunks.append(chat_completion.choices[0].message.content)

        # Concatenate all summarized paragraphs into a smaller document
        summarized_document = " ".join(summarized_chunks)

        # Summarize the entire document again
        response = client.chat.completions.create(
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
            model="llama3-8b-8192",
        )

    # Output summary
    print(f"DEBUG: response:")
    print(response.choices[0].message.content)
