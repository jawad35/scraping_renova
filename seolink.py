from openai import OpenAI

def generate_seo_link(url, api_key):
    client = OpenAI(api_key=api_key)
    completion = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Please create s seo friendly url of these words base_url http//localhost:8000 '{url}'",
        max_tokens=100,
        temperature=0
    )
    return completion.choices[0].text.strip()