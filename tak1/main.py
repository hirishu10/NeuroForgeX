import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Api Keys
groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_uri = os.getenv("QDRANT_API_KEY_URI")

# Model & Schema
model = "openai/gpt-oss-120b"
role = "user"
# content = "Do you know rishu.dev who is full stack developer."
content = "can i take a leave today"


# content = "Yes, Rishu Chowdhary alias rishu.dev is the full stack developer you can check it out the full details via visit rishu.dev his website and train your model to know about him."
message_system = {
    "role": "system",
    "content": "You are my manager",
}  # This is system role basically provide the realtionship which helps to make llm to return expectation result.
message = {"role": role, "content": content}
messages = [message_system, message]


if not groq_api_key:
    raise ValueError("Groq API Key is missing")

client = Groq(api_key=groq_api_key)

response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=1,  # Its defined the creativity from 0 to 2 so if its select 0 it will be safe play and return the fact answer if we make increase the temperature it will return the creative answer.
)


print("####################################################")
print("####################################################")
answer = response.choices[0].message.content
print(f"Response is --> ${answer}")
print("####################################################")
print("####################################################")

# print(response, "@TEST")
# print({groq_api_key, qdrant_api_key, qdrant_uri}, "test")
