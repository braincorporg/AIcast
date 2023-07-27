import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import requests

load_dotenv()
app = FastAPI()

function_descriptions = [
    {
        "name": "extract_info_from_text",
        "description": "describe & extract key info from any text, such as topic, keywords, and important details so you can create a complete blog post about that subject",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Identify the topic of the text"
                },                                        
                "keywords": {
                    "type": "string",
                    "description": "Extract all relevant keywords from text and add some that you think should also be used."
                },
                "details":{
                    "type": "string",
                    "description": "Try to identify all the important details about that subject, what is the vision, what are the intent of the text so on and so forth"
                },
                "blogPost": {
                    "type": "string",
                    "description": "Create a blog post based on all the informations you have about that subject, including keywords and technical details. Do not provide layout or line break."
                },
            },
            "required": ["topic", "keywords", "details", "blogPost"]
        }
    }
]


def write_to_airtable(apiKey, baseId, topic, keywords, details, blogPost):
    # use apiKey, baseId, tableName in your function
    AIRTABLE_API_KEY = apiKey
    AIRTABLE_BASE_ID = baseId
    AIRTABLE_TABLE_NAME = "result"
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "records": [
            {
                "fields": {
                    "topic": topic,
                    "keywords": keywords,
                    "details": details,
                    "blogPost": blogPost
                }
            }
        ]
    }

    response = requests.post(
        f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}',
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


class texte(BaseModel):
     content: str
     apiKey: str
     baseId: str
     openaiApiKey: str

@app.get("/")
def read_root():
 return {"Hello": "World"}

@app.post("/")
def analyse_email(text: texte):
 openai.api_key = text.openaiApiKey
 content = text.content
 query = f"Please describe and extract key information from this text: {content} "

 messages = [{"role": "user", "content": query}]

 response = openai.ChatCompletion.create(
     model="gpt-4-0613",
     messages=messages,
     functions = function_descriptions,
     function_call="auto"
 )

 arguments = response.choices[0]["message"]["function_call"]["arguments"]
 print(arguments)
 topic = eval(arguments).get("topic")
 keywords = eval(arguments).get("keywords")
 details = eval(arguments).get("details")
 blogPost = eval(arguments).get("blogPost")
 blogPost = '"""' + blogPost + '"""'
 print(blogPost)
 write_to_airtable(text.apiKey, text.baseId, topic, keywords, details, blogPost)
 return {
     "topic": topic,
     "keywords": keywords,
     "details": details,
     "blogPost": blogPost,

 }

