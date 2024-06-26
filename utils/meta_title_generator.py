import openai
from dotenv import load_dotenv
load_dotenv()
import os
def meta_title_generator(title):
    try:
        client = openai.Client(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please rewrite the title precisly'{title}'",
            max_tokens=200,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return title 
    