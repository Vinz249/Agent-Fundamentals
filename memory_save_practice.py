from groq import Groq
import os
from dotenv import load_dotenv

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


memory = []

def chat(input):
    memory.append(
        {
            "role": "user",
            "content": input
        }
    )

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        max_tokens = 300,
        messages = memory
    )

    g_out = response.choices[0].message.content

    memory.append(
        {
             "role": "assistant",
            "content": g_out
        }
    )

    return g_out


print(chat("Hi model, My name is Vinayak! what is your name?"))
print(chat("What is my name?"))