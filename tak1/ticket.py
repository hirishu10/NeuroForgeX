import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()


class TicketSystem(BaseModel):
    name: str
    phone: int
    email: str
    issue: str
    # suspect_information: str


schema = TicketSystem.model_json_schema()

response_format = {"type": "json_object"}

# Api Keys
groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_uri = os.getenv("QDRANT_API_KEY_URI")

# Model & Schema
model = "openai/gpt-oss-120b"
role = "user"
# content = "Do you know rishu.dev who is full stack developer."
content = "my name is Rishu Chowdhary, i have my lost my mobile phone while traveling from public bus, my mobile number is 9836110678, i would like to raise a complain from my email id hi.10rishu@gmail.com. i also noticed that some person is sitted beside me he take the phone."


# content = "Yes, Rishu Chowdhary alias rishu.dev is the full stack developer you can check it out the full details via visit rishu.dev his website and train your model to know about him."
message_system_one = {
    "role": "system",
    "content": f"""
    I have making the ticket system hence retrieve the personal and important imformation from {content}
    """,
}

message_system_two = {
    "role": "system",
    "content": f"""
Extract the personal information from the ticket system strictly based on this schema here {schema} and return me as json output.
""",
}


message = {"role": role, "content": content}
messages = [message_system_one, message_system_two, message]


if not groq_api_key:
    raise ValueError("Groq API Key is missing")

client = Groq(api_key=groq_api_key)

response = client.chat.completions.create(
    model=model,
    messages=messages,
    response_format=response_format,  # It will return the output format
    # temperature=1,  # Its defined the creativity from 0 to 2 so if its select 0 it will be safe play and return the fact answer if we make increase the temperature it will return the creative answer.
)


print("####################################################")
print("####################################################")
answer = response.choices[0].message.content
print(f"Response is --> ${answer}")
print("####################################################")
print("####################################################")

# print(response, "@TEST")
# print({groq_api_key, qdrant_api_key, qdrant_uri}, "test")

import json

# raw_json = f"{answer}"
raw_json = answer
data_file = json.loads(raw_json)
ticket_data = TicketSystem(**data_file)

print(f"N - {ticket_data.name}")
print(f"P - {ticket_data.phone}")
print(f"E - {ticket_data.email}")
print(f"I - {ticket_data.issue}")
