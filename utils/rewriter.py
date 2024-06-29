import openai
from dotenv import load_dotenv
load_dotenv()
import os

def rewriter(description):
    try:
        client = openai.Client(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Rewrite the content of each HTML tag while ensuring the meaning remains consistent. Focus on varying sentence structure, synonyms, and phrasing to create distinct but semantically equivalent content'{description}'",
            max_tokens=2000,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error decreasing price: {e}")
        return description