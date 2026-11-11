import os
import time
import re
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
# response_format = {"type": "json_object"}

if not groq_api_key:
    raise ValueError("Groq API Key is missing")

client = Groq(api_key=groq_api_key)


# Helper Tools which will be callable from the LLM
def get_product_price(product):
    if product == "iPhone 17":
        return 3000
    elif product == "iPhone 15":
        return 2000
    else:
        return "Not available the product you are looking"


def calculator(exporession):
    try:
        return eval(exporession)
    except:
        return "Cacl error"


tools = {"get_product_price": get_product_price, "calculator": calculator}

system_prompt = """
You are a shopping assistant.

You have this tools:

get_product_price(product)
calculator(expression)
IMPORTANT:
Call tools exactly like these examples:

Action: get_product_price("iPhone 17")
Action: calculator("5000 - 1000")

Never write:
get_product_price(product="iPhone 17")

Never write:
calculator(expression="5000 - 1000")

Follow this rules:
1. Decide what you need to do next.
2. Call ONLY ONE tool at time.
3. After writing an Action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an Observation.
6. Then decide your next action.
7. When the task is complete, give the Final Answer.

Format:

Thought: what you need to do 
Action: tool_name(argument)

When finished:

Final Answer: your answer
"""


def run_agent(question):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    for step in range(5):
        print("\n---------------")
        print(f"Step-{step + 1}")
        print("\n---------------")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        answer = response.choices[0].message.content

        if "Final Answer:" in answer:
            break

        match = re.search(r"Action:\s*(\w+)\((.*?)\)", answer)

        if match:

            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip('"')

            if tool_name in tools:

                tool = tools[tool_name]

                observation = tool(tool_input)

            else:
                observation = "Tool not found"

            print("Observation", observation)

            messages.append({"role": "assistant", "content": answer})

            messages.append(
                {"role": "user", "content": "Observation" + str(observation)}
            )

            time.sleep(5)


prompt = "I have to buy iphone 16 can i buy if i have 2000 ?"

run_agent(prompt)


# import os
# import re
# import ast
# import operator
# import time

# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# # API Configuration
# groq_api_key = os.getenv("GROQ_API_KEY")

# if not groq_api_key:
#     raise ValueError("Groq API Key is missing")

# client = Groq(api_key=groq_api_key)

# # Model
# model = "openai/gpt-oss-120b"


# # -----------------------------
# # TOOL 1: Product Price
# # -----------------------------


# def get_product_price(product):

#     products = {"iphone 17": 3000, "iphone 16": 2500, "iphone 15": 2000}

#     product = product.strip().lower()

#     return products.get(product)


# # -----------------------------
# # TOOL 2: Safe Calculator
# # -----------------------------


# def calculator(expression):

#     allowed_operators = {
#         ast.Add: operator.add,
#         ast.Sub: operator.sub,
#         ast.Mult: operator.mul,
#         ast.Div: operator.truediv,
#     }

#     try:
#         tree = ast.parse(expression, mode="eval")

#         def calculate(node):

#             if isinstance(node, ast.Expression):
#                 return calculate(node.body)

#             if isinstance(node, ast.Constant):
#                 if isinstance(node.value, (int, float)):
#                     return node.value
#                 raise ValueError("Invalid number")

#             if isinstance(node, ast.BinOp):
#                 op = type(node.op)

#                 if op not in allowed_operators:
#                     raise ValueError("Operator not allowed")

#                 left = calculate(node.left)
#                 right = calculate(node.right)

#                 return allowed_operators[op](left, right)

#             raise ValueError("Invalid expression")

#         return calculate(tree)

#     except Exception as e:
#         return f"Calculator error: {e}"


# # -----------------------------
# # TOOL REGISTRY
# # -----------------------------

# tools = {"get_product_price": get_product_price, "calculator": calculator}


# # -----------------------------
# # SYSTEM PROMPT
# # -----------------------------

# system_prompt = """
# You are a shopping assistant.

# Available tools:

# 1. get_product_price(product)
# 2. calculator(expression)

# Rules:

# 1. Decide what to do next.
# 2. Call only ONE tool at a time.
# 3. Never invent tool results.
# 4. Wait for an Observation before continuing.
# 5. When finished, provide a Final Answer.

# Tool calling format:

# Thought: I need to check the product price.
# Action: get_product_price("iPhone 16")

# OR

# Thought: I need to calculate the remaining balance.
# Action: calculator("2000 - 2500")

# Never use named arguments.

# When finished:

# Final Answer: Your answer here.

# IMPORTANT:
# If a product price is None, tell the user that
# the product price is unavailable.
# """


# # -----------------------------
# # AGENT FUNCTION
# # -----------------------------


# def run_agent(question):

#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": question},
#     ]

#     for step in range(5):

#         print(f"\n---------- STEP {step + 1} ----------")

#         response = client.chat.completions.create(
#             model=model, messages=messages, temperature=0
#         )

#         answer = response.choices[0].message.content or ""

#         print("\nLLM:", answer)

#         # Check final answer
#         if "Final Answer:" in answer:

#             final_answer = answer.split("Final Answer:", 1)[1].strip()

#             print("\nFINAL RESULT:", final_answer)

#             return final_answer

#         # Extract Action
#         match = re.search(r"Action:\s*(\w+)\((.*)\)\s*$", answer, re.MULTILINE)

#         if not match:

#             messages.append({"role": "assistant", "content": answer})

#             messages.append(
#                 {
#                     "role": "user",
#                     "content": "Please provide a valid Action or Final Answer.",
#                 }
#             )

#             continue

#         tool_name = match.group(1)

#         raw_input = match.group(2).strip()

#         # Validate tool
#         if tool_name not in tools:

#             observation = "Tool not found"

#         else:

#             try:

#                 tool_input = ast.literal_eval(raw_input)

#                 if not isinstance(tool_input, str):
#                     raise ValueError("Tool argument must be a string")

#                 tool = tools[tool_name]

#                 observation = tool(tool_input)

#             except Exception as e:

#                 observation = f"Tool execution error: {e}"

#         print("\nObservation:", observation)

#         # Update conversation
#         messages.append({"role": "assistant", "content": answer})

#         messages.append({"role": "user", "content": f"Observation: {observation}"})

#     print("\nAgent stopped: Maximum steps reached.")

#     return None


# # -----------------------------
# # RUN AGENT
# # -----------------------------

# # prompt = "I have to buy iPhone 16. Can I buy it if I have 2000?"
# prompt = "I need to buy iphone 17. i have 8000"

# run_agent(prompt)
