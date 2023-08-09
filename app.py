import openai
from dotenv import load_dotenv
import chainlit as c1
from src.llm import chat_completion_request,messages,functions
#from src.sys_config import conv_prompt
from src.utils import get_current_weather
import json
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

import json

def execute_function_call(assistant_message):

    arguments = assistant_message['function_call']['arguments']
    location = arguments.split('"location": "')[1].split('"')[0]
    results=get_current_weather(location)

    return results

def get_natural_response(content):
    convert_prompt = f"convert this results from weather api to a natural english sentence containing the temperature and other important metrics also dont mention country and state and also tell what we can do in that based on your knowlodge like 6-7 place to see and but also suggests 3-4 activities in bulltet points tailored to the given climatic conditions and dont mention you are using Weather API and use word climate instead of weather in response {content}"
    messages.append({"role": "user", "content": convert_prompt})
    convert_prompt_response = chat_completion_request(messages=messages)
    print(f"\n>>>> recieved message: {convert_prompt_response.json()}")
    new_assistant_message = convert_prompt_response.json()["choices"][0]["message"]
    messages.append(new_assistant_message)
    content = new_assistant_message["content"]
    print(f"\n>>>> natural response: \n{content}")
    return content

@c1.on_chat_start
async def start():
    #chain = qa_bot()
    msg = c1.Message(content="Starting the bot...")
    await msg.send()
    msg.content = "Hi, Welcome to ClimateGPT created by Kartik. What is your query?"
    await msg.update()
    
    

    
@c1.on_message
async def main(message:str):
    messages.append({"role":"user","content":message})

    chat_response=chat_completion_request(messages=messages,functions=functions)

    assistant_message = chat_response.json()["choices"][0]["message"]
    if assistant_message.get("function_call"):
        result=execute_function_call(assistant_message)
        content=json.dumps(result)
        content=get_natural_response(content)
    else:
        messages.append(assistant_message)
        content = assistant_message["Hey I am Weather-bot created by Kartik so I can only answer temperature if you give me the location: Sorry"]

    #print(f"\n>>>> Chat response: \n{content}")


    await c1.Message(
        content=content
    ).send()

