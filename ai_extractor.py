from dotenv import load_dotenv
from openai import OpenAI

from models import CVData


load_dotenv()

client = OpenAI()


def extract_cv_data(text):
    response = client.responses.parse(
        model="gpt-6-luna",
        input=[
            {
                "role": "system",
                "content": """
You extract structured information from CVs.

Only extract information that is actually present in the CV.
Do not invent missing information.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        text_format=CVData,
    )

    return response.output_parsed