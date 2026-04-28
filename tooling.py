from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Step 1: Tell the LLM what tools exist
# The LLM reads these descriptions and decides when to use them
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_customer_risk",
            "description": "Checks the risk score of a customer by their ID. Use this when you need to assess customer risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The unique customer identifier"
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
]

# Step 2: Your actual function — you control what this does
def check_customer_risk(customer_id):
    fake_database = {
        "C001": {"name": "John Murphy", "risk_score": 85, "flags": ["large_transactions"]},
        "C002": {"name": "Sarah O'Brien", "risk_score": 12, "flags": []},
        "C003": {"name": "James Walsh", "risk_score": 67, "flags": ["foreign_transfers"]},
    }
    return fake_database.get(customer_id, {"error": "Customer not found"})

# Step 3: The agent loop
def run_agent(user_query):
    messages = [{"role": "user", "content": user_query}]

    # First call — LLM decides if it needs a tool
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        tools=tools,
        messages=messages
    )

    finish_reason = response.choices[0].finish_reason

    # Did the LLM ask to use a tool?
    if finish_reason == "tool_calls":
        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_input = json.loads(tool_call.function.arguments)

        print(f"  → Agent calling tool: {tool_name}")
        print(f"  → With input: {tool_input}")

        # Run YOUR function with what the LLM asked for
        tool_result = check_customer_risk(tool_input["customer_id"])
        print(f"  → Tool returned: {tool_result}")

        # Add everything back to the conversation
        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        })

        # Second call — LLM reasons with the result
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            tools=tools,
            messages=messages
        )

        return final_response.choices[0].message.content

    # LLM answered without needing a tool
    return response.choices[0].message.content


print("Query 1:")
print(run_agent("What is the risk profile of customer C001? Should I be concerned?"))
print("\nQuery 2:")
print(run_agent("Is customer C002 high risk?"))
print("\nQuery 3:")
print(run_agent("What is the capital of France?"))  # Should NOT call the tool