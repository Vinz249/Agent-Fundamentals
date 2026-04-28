from groq import Groq
import os
from dotenv import load_dotenv

client = Groq(api_key= os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model = "llama-3.3-70b-versatile",
    max_tokens = 200,
    messages = [{ "role": "user", "content": "Goku vs Luffy who will win?"}]
    
)

answer = response.choices[0].message.content
print(answer)
