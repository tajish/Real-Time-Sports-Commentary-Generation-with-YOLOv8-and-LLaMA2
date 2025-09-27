from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv
import json

from langchain_groq import ChatGroq

load_dotenv()

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

def generate_commentary(speed_window, start, end):
    Expert_BOT_TEMPLATE = """
    You're a football match commentator.
    Analyze the ball's speed between frames {start_frame} and {end_frame}: {speed_window}.
    And Tennis commentary under 30 words:
    Ball speed {speed_window}.
    Energetic, exciting tone. No frame references.
    """

    prompt = ChatPromptTemplate.from_template(Expert_BOT_TEMPLATE)

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.8)

    
    chain = prompt | llm | StrOutputParser()

    
    result = chain.invoke({"end_frame":end,"speed_window": speed_window,"start_frame":start})

    return result  
