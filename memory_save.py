from groq import Groq
import os
from dotenv import load_dotenv

client = Groq(api_key = os.environ.get("GROQ_API_KEY"))

conv_memory = []


def chat(user_input):
    conv_memory.append(
        {
            "role":"user",
            "content": user_input
        }
    )


    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        max_tokens = 300,
        messages = conv_memory
    )

    assistant_reply = response.choices[0].message.content
    conv_memory.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )

    return assistant_reply


print(chat("My name is Vinayak and I am studying Masters in AI"))
print(chat("What is Naredra Modi father name"))
print("...............")
print(chat("What is my name and what am I doing?"))
