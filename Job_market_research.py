from groq import Groq
import os
import json
from tavily import TavilyClient

# Connect to API
client  =  Groq(api_key = os.environ.get("GROQ_API_KEY"))

tavily_client = TavilyClient(api_key = os.environ.get("TAVILY_API_KEY"))






# Define the tool

tools =[
{
    "type":"function",
    "function":{
        "name":"get_job_market_trends",
        "description": "Fetch the top companies with openings, average salaies and skills requried for this job role for freshers in the location",
        "parameters":{
            "type":"object",
            "properties":{
                "job_role":{
                    "type":"string",
                    "description": "The name of the job role which is to be searched"
                },
                "location":{
                    "type":"string",
                    "description": "The name of the location"
                }
            },
            "required":["job_role","location"]
        }
    }
}
]

# Defining tool function
def get_job_market_trends(search_query):
 results = tavily_client.search(query= search_query)
 cleaned = [{"title": r["title"], "content": r["content"]} 
               for r in results["results"]]
 return cleaned

# Tool routing not needed as I have one tool only


def run_agent(user_query):
  
 # Define memory and give query
  messages = [{"role":"user","content":user_query} ]

  response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        max_tokens = 1000,
        tools = tools,
        temperature = 0.2,
        messages = messages
  )
  response_message = response.choices[0].message
  finish_reason = response.choices[0].finish_reason
  
  if finish_reason == "tool_calls":
     messages.append(response_message)
     for tool_call in response_message.tool_calls:
       tool_name = tool_call.function.name
       tool_input = json.loads(tool_call.function.arguments)
       print(f"Tool called: {tool_name} with input: {tool_input}")
       if tool_name == "get_job_market_trends":
             search_query = f"{tool_input['job_role']} fresher jobs {tool_input['location']} 2026 salary skills"
             tool_result = get_job_market_trends(search_query)
             messages.append(
                {"role": "tool",
                 "tool_call_id": tool_call.id,
                 "content": json.dumps(tool_result)})


            # After tool call, run the agent again with the tool result in context
             final_response = client.chat.completions.create(
               model = "llama-3.3-70b-versatile",
               max_tokens = 1000,
               temperature = 0.2,
               tools = tools,
               messages = messages
             )
       
             return final_response.choices[0].message.content
  else:
        return response_message.content
       

print("Hi USER!!! This is the Job Market Research for Freshers Agent \n ")
query = input("Enter your query:\t")
print(run_agent(query))
      
    

