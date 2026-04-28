from groq import Groq
import os
from dotenv import load_dotenv
import json

client  =  Groq(api_key = os.environ.get("GROQ_API_KEY"))

# Creating city weather and flight database

city_weather = {
    "dublin": {"weather": "raining"},
    "delhi": {"weather": "sunny"},
    "paris": {"weather": "cloudy"}
}

flight_price = {
    "dublin": {"price_eur": "45","airline":"Ryanir"},
    "delhi": {"price_eur": "89","airline":"Qatar"},
    "paris": {"price_eur": "67","airline":"Swiss"}
}


# Define Tools

tools =[
    {
        "type":"function",
        "function":{
            "name":"get_city_weather",
            "description": "Fetch the weather condition for a city",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description": "The name of the city"
                    }
                },
                "required":["city"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_flight_price",
            "description": "Get the cheapest available flight price to a destination city",
            "parameters":{
                "type":"object",
                "properties":{
                    "destination":{
                        "type":"string",
                        "description": "The name of the destination"
                    }
                },
                "required":["destination"]
            }
        }
        

    }
]

# Functions

def get_city_weather(city,city_weather):
    return city_weather.get(city.lower(),{"error":"city not found"})

def get_flight_price(destination,flight_price):
    return flight_price.get(destination.lower(),{"error":"destination not found"})


# Tools router

def run_tools(tool_name,tool_input):
    if tool_name == "get_city_weather":
        return get_city_weather(tool_input["city"],city_weather)
    
    elif tool_name == "get_flight_price":
        return get_flight_price(tool_input["destination"],flight_price)
                


# agent function

def run_agent(user_query):
    messages = [{"role": "user", "content": user_query}]

    # First run — LLM decides whether it needs a tool
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        max_tokens = 500,
        tools = tools,
        messages = messages
    )

    finish_reson = response.choices[0].finish_reason

    if finish_reson == "tool_calls":
        messages.append(response.choices[0].message)

        for tool_call in response.choices[0].message.tool_calls:
        
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            print(f"  → Agent chose tool: {tool_name}")
            print(f"  → Input: {tool_input}")

            tool_result = run_tools(tool_name, tool_input)
            print(f"  → Result: {tool_result}")

            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

        # Second run — LLM answers using the tool result
        final_response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            max_tokens = 500,
            tools = tools,
            messages = messages
        )

        return final_response.choices[0].message.content

    return response.choices[0].message.content




# These four queries test different things
print("Query 1 — should use get_weather:")
print(run_agent("What's the weather like in Delhi?"))

print("\nQuery 2 — should use get_flight_price:")
print(run_agent("How much is a flight from Dublin to Paris?"))

print("\nQuery 3 — should use BOTH tools:")
print(run_agent("I'm thinking of going to Delhi this weekend. What's the weather and what will a flight cost me?"))

print("\nQuery 4 — should use neither tool:")
print(run_agent("What year did Ireland join the EU?"))