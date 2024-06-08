from openai import OpenAI

def generate_rewrite(description, api_key):
    print(description)
    client = OpenAI(api_key=api_key)
    completion = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Please generate a meta description within 60 to 150 characters using all paramters '{description}'",
        max_tokens=100,
        temperature=0
    )
    return completion.choices[0].text.strip()