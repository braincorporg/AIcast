import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
                    "description": "Create a blog post based on all the informations you have about that subject, including keywords and technical details"
                },
            },
            "required": ["topic", "keywords", "details", "blogPost"]
        }
    }
]

class Texte(BaseModel):
     content: str
    
@app.get("/")
def read_root():
 return {"Hello": "World"}

@app.post("/")
def analyse_email(text: Texte):
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
 topic = eval(arguments).get("topic")
 keywords = eval(arguments).get("keywords")
 details = eval(arguments).get("details")
 blogPost = eval(arguments).get("blogPost")

 return {
     "topic": topic,
     "keywords": keywords,
     "details": details,
     "blogPost": blogPost,

 }

