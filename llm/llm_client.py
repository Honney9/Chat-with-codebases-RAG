import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(prompt: str):

    #  Sends prompt to Groq LLaMA-3 and returns response.

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,   # Low = factual, less hallucination
        max_tokens=700
    )

    return response.choices[0].message.content
