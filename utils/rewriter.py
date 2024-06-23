import openai
from dotenv import load_dotenv
load_dotenv()
import os

def rewriter(description):
    try:
        client = openai.Client(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please rewrite the following HTML content, changing the text within the HTML tags but keeping the same meaning and don't skip anything return data in object form not string like p1:this is sample paragaraph:'{description}'",
            max_tokens=2000,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error decreasing price: {e}")
        return description