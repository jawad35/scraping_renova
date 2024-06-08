import openai
from dotenv import load_dotenv
load_dotenv()
import os

def meta_description_generator(description):
    try:
        client = openai.Client(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"based on provided tables data ready comprehensive meta description that highlights key features from each table with english words must cover within 100 characters only'{description}'",
            max_tokens=150,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error decreasing price: {e}")
        return description