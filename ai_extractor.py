from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()


def extract_structured_data(text: str, schema: type[BaseModel]):
    response = client.responses.parse(
        model="gpt-6-luna",
        input=[
            {
                "role": "system",
                "content": """
Extract structured information from the provided document.

Only extract information that is actually present.
Do not invent missing information.
Follow the provided output schema exactly.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        text_format=schema,
    )

    return response.output_parsed