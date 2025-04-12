import fitz
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import tiktoken
from difflib import SequenceMatcher
import json
import re

load_dotenv()


def extract_text(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    :param file_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_summary(text: str) -> str:
    """
    Generate a summary of the given text.
    :param text: Text to summarize.
    :return: Summary of the text.
    """
    try:
        prompt_template = """
            You are a medical report analysis expert. Your task is to carefully analyze the following portion of a medical report and extract:
            1. Key medical points (e.g., diagnosis, test results)
            2. Highlights (important findings)
            3. Precautions or suggested actions

            Only return a JSON like:
            Only return a valid JSON like:
            {{
            "key_points": ["<short summary string>", "..."],
            "highlights": ["<highlighted insights>", "..."],
            "precautions": ["<precautionary advice>", "..."]
            }}

            Here's the text:
            {text}
            """
        formatted_prompt = prompt_template.format(text=text)
        client = AzureOpenAI(api_key=os.environ.get("AZURE_OPEN_AI_API_KEY"),
            azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
            api_version=os.environ.get("APIVERSION")
            )
        response = client.chat.completions.create(
            model="gpt-4o",  # or your deployed model on Azure
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content  # Return the first 100 characters as a mock summary.
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""

def sliding_window_chunks(text, max_tokens=3000, overlap_tokens=500):
    encoding = tiktoken.encoding_for_model("gpt-4")
    words = text.split()
    
    chunks = []
    start = 0
    while start < len(words):
        chunk_words = words[start:]
        token_estimate = len(encoding.encode(" ".join(chunk_words)))
        
        if token_estimate <= max_tokens:
            chunks.append(" ".join(chunk_words))
            break
        
        # truncate chunk at max_tokens
        current_chunk = []
        current_tokens = 0
        for word in chunk_words:
            t = len(encoding.encode(word + " "))
            if current_tokens + t > max_tokens:
                break
            current_chunk.append(word)
            current_tokens += t

        chunks.append(" ".join(current_chunk))
        start += len(current_chunk) - (overlap_tokens // 4)  # backward step to retain context overlap

    return chunks


def remove_duplicates(list1):
    unique = []
    for item in list1:
        if not any(SequenceMatcher(None, item, existing).ratio() > 0.9 for existing in unique):
            unique.append(item)
    return unique

def clean_json_response(response: str) -> dict:
    """
    Clean OpenAI response and parse JSON.
    """
    try:
        cleaned = re.sub(r'```(?:json)?\n(.*?)```', r'\1', response, flags=re.DOTALL).strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Raw response:", response)
        return {}

def analyze_pdf_report(file_path):
    text = extract_text(file_path)
    chunks = sliding_window_chunks(text)
    key_points, highlights, precautions = [], [], []
    
    for chunk in chunks:
        try:
            summary = get_summary(chunk)
            parsed = clean_json_response(summary)
            
            key_points.extend(parsed.get("key_points", []))
            highlights.extend(parsed.get("highlights", []))
            precautions.extend(parsed.get("precautions", []))
        
        except json.JSONDecodeError:
            print("Error: Could not parse JSON from response")
            print(summary)
    
    # Deduplicate results
    final_result = {
        "key_points": remove_duplicates(key_points),
        "highlights": remove_duplicates(highlights),
        "precautions": remove_duplicates(precautions)
    }
    
    return final_result
















































# import fitz  # PyMuPDF
# from openai import AzureOpenAI
# from dotenv import load_dotenv
# import os
# import tiktoken
# from difflib import SequenceMatcher
# import json
# import re
# import time

# load_dotenv()

# def extract_text(file_path: str) -> str:
#     """
#     Extract text from a PDF file using PyMuPDF (fitz).
#     :param file_path: Path to the PDF file.
#     :return: Extracted text as a string.
#     """
#     text = ''
#     with fitz.open(file_path) as doc:
#         for page in doc:
#             text += page.get_text()
#     return text


# def get_summary(text: str) -> str:
#     try:
#         print("----------------------------Generating Summary----------------------------")
#         print("Text length:", len(text))
#         start_time = time.time()  # Start timer for API call
        
#         prompt_template = '''
#         You are a medical report analysis expert. Your task is to carefully analyze the following portion of a medical report and extract:
#         1. Key medical points (e.g., diagnosis, test results)
#         2. Highlights (important findings)
#         3. Precautions or suggested actions

#         Only return a valid JSON like:
#         {{
#           "key_points": ["<short summary string>", "..."],
#           "highlights": ["<highlighted insights>", "..."],
#           "precautions": ["<precautionary advice>", "..."]
#         }}

#         Here's the text:
#         {text}
#         '''
#         formatted_prompt = prompt_template.format(text=text)
#         print("Formatted prompt length:", len(formatted_prompt))
#         print("Formatted prompt:", formatted_prompt)
        
#         # Timeout added to prevent the request from hanging
#         client = AzureOpenAI(
#             api_key=os.environ.get("AZURE_OPEN_AI_API_KEY"),
#             azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
#             api_version=os.environ.get("APIVERSION")
#         )

#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": formatted_prompt}],
#             temperature=0.7,
#             timeout=60  # Set timeout to 60 seconds
#         )
        
#         end_time = time.time()  # End timer for API call
#         print(f"API call duration: {end_time - start_time} seconds")
#         print("Response length:", len(response.choices[0].message.content))
#         return response.choices[0].message.content

#     except Exception as e:
#         print(f"Error generating summary: {e}")
#         return ""

# # def get_summary(text: str) -> str:
# #     """
# #     Generate a summary of the given text using Azure OpenAI.
# #     :param text: Text to summarize.
# #     :return: Summary as a JSON string.
# #     """
# #     try:
# #         print("----------------------------Generating Summary----------------------------")
# #         print("Text length:", len(text))
# #         prompt_template = '''
# #         You are a medical report analysis expert. Your task is to carefully analyze the following portion of a medical report and extract:
# #         1. Key medical points (e.g., diagnosis, test results)
# #         2. Highlights (important findings)
# #         3. Precautions or suggested actions

# #         Only return a valid JSON like:
# #         {{
# #           "key_points": ["<short summary string>", "..."],
# #           "highlights": ["<highlighted insights>", "..."],
# #           "precautions": ["<precautionary advice>", "..."]
# #         }}

# #         Here's the text:
# #         {text}
# #         '''
# #         formatted_prompt = prompt_template.format(text=text)
# #         print("Formatted prompt length:", len(formatted_prompt))
# #         print("Formatted prompt:", formatted_prompt)
# #         client = AzureOpenAI(
# #             api_key=os.environ.get("AZURE_OPEN_AI_API_KEY"),
# #             azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
# #             api_version=os.environ.get("APIVERSION")
# #         )

# #         response = client.chat.completions.create(
# #             model="gpt-4o",
# #             messages=[{"role": "user", "content": formatted_prompt}],
# #             temperature=0.7
# #         )
# #         print("Response length:", len(response.choices[0].message.content))
# #         return response.choices[0].message.content

# #     except Exception as e:
# #         print(f"Error generating summary: {e}")
# #         return ""

# def sliding_window_chunks(text, max_tokens=3000, overlap_tokens=500):
#     """
#     Break text into overlapping chunks based on token estimates.
#     """
#     encoding = tiktoken.encoding_for_model("gpt-4")
#     words = text.split()
#     chunks = []
#     start = 0

#     while start < len(words):
#         current_chunk = []
#         current_tokens = 0
#         for i in range(start, len(words)):
#             word = words[i]
#             t = len(encoding.encode(word + ' '))
#             if current_tokens + t > max_tokens:
#                 break
#             current_chunk.append(word)
#             current_tokens += t
#         chunks.append(' '.join(current_chunk))
#         start += max(1, len(current_chunk) - overlap_tokens // 4)  # Avoid infinite loops

#     return chunks

# def remove_duplicates(list1):
#     """
#     Remove near-duplicate strings using similarity ratio.
#     """
#     try:
#         unique = []
#         for item in list1:
#             if not any(SequenceMatcher(None, item, existing).ratio() > 0.9 for existing in unique):
#                 unique.append(item)
#         return unique
#     except Exception as e:
#         print(f"Error removing duplicates: {e}")
#         return list1

# def clean_json_response(response: str) -> dict:
#     """
#     Clean OpenAI response and parse JSON.
#     """
#     try:
#         cleaned = re.sub(r'```(?:json)?\n(.*?)```', r'\1', response, flags=re.DOTALL).strip()
#         return json.loads(cleaned)
#     except Exception as e:
#         print(f"Error parsing JSON: {e}")
#         print("Raw response:", response)
#         return {}

# def analyze_pdf_report(file_path):
#     """
#     Full pipeline: Extract text, split into chunks, summarize each, merge results.
#     """
#     try:
#         print("----------------------------Analyzing PDF Report----------------------------")
#         text = extract_text(file_path)
#         print("Extracted text from PDF.")
#         print(text)
#         chunks = sliding_window_chunks(text)
#         print(len(chunks), "chunks created.")
#         key_points, highlights, precautions = [], [], []

#         for chunk in chunks:
#             print("Chunk length:", len(chunk))
#             summary = get_summary(chunk)
#             parsed = clean_json_response(summary)

#             key_points.extend(parsed.get("key_points", []))
#             highlights.extend(parsed.get("highlights", []))
#             precautions.extend(parsed.get("precautions", []))

#         final_result = {
#             "key_points": remove_duplicates(key_points),
#             "highlights": remove_duplicates(highlights),
#             "precautions": remove_duplicates(precautions),
#         }

#         return final_result

#     except Exception as e:
#         print(f"Error analyzing PDF report: {e}")
#         return {
#             "key_points": [],
#             "highlights": [],
#             "precautions": [],
#         }
