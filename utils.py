import json,re,os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate 
from pydantic import BaseModel,field_validator,Field
from typing import List


# *********** load_dotenv() and checking ******************
load_dotenv()

if not os.getenv('GOOGLE_API_KEY'):
    raise EnvironmentError("API key not found")

# ************** Creating MCQ Question Model **************

class MCQQuestion(BaseModel):
    # Note : model use the description to generate the proper result so write it perfectly
    question: str = Field(description="The question text")      
    options: List[str] = Field(description="list of 4 options")
    correct_answer: str = Field(description="correct answer from the options")
    
#********* adding field validator for 'question' field *****
"""
    field validator will get automatically called when model sends response
    and if response is in dict then simply convert it to string
    and same applies for options  
    
    mode='before' means:
    Run this validator BEFORE Pydantic checks the data type
    
    Without mode='before'
        Pydantic sees dict instead of string
        Immediately throws error
        Your validator never runs
"""

@field_validator('question',mode='before')
def clean_question(cls,v):
    if isinstance(v,dict):
        return v.get('description',str(v))
    return str(v)

@field_validator('options',mode='before')
def check_options(cls,v):
    if not isinstance(v,list) or len(v) != 4:
        raise ValueError("options must have exactly 4 items")
    return [str(x) for x in v]


#=================== similar things for fill in the blanks question model===

class FillBlankQuestion(BaseModel):
    question: str = Field(description="question with '_____' as the blank")
    answer: str = Field(description="correct word or phrase for the blank")

@field_validator('question',mode='before')
def clean_question(cls,v):
    if isinstance(v,dict):
        return v.get('description',str(v))
    return str(v)

@field_validator('question',mode='after')
def check_blank(cls,v):
    if '_____' not in v: 
        raise ValueError("question must have '_____' as blank marker")
    return v 


    
# ********* General functions to extract incoming data from LLM ***

def extract_text(response) -> str:
    content = response.content
    if isinstance(content , str):
        return content
    if isinstance(content , list):
        parts = []
        for block in content:
            if isinstance(block , str):
                parts.append(block)
            elif isinstance(block , dict):
                parts.append(block.get('text',''))
            elif hasattr(block , 'text'):
                parts.append(block.text)
        return ' '.join(parts)
    return str(content)

##**** extracts json object from LLM output 

def extract_json(text: str) -> dict: 
    # remove markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`")
    
    # try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # fallback: grab first {...} block
    match = re.search(r'\{.*\}' , text , re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"could not find valid JSON in response:\n{text[:300]}")




#=======================================================================
# ===================Question Generator Class ==========================
#=======================================================================



class QuestionGenerator: 
    
    def __init__(self):
        self.chat_model = ChatGoogleGenerativeAI(
            model = "gemini-3-flash-preview",
            temperature=0.7,
            google_api_key = os.getenv('GOOGLE_API_KEY')
        )
    
    ######## MCQ Question method *****************
    
    def generate_mcq(self,topic: str, difficulty: str = 'medium') -> MCQQuestion:
        prompt = PromptTemplate(
            template = """Generate a {difficulty} difficulty MCQ about: {topic}

            Return ONLY a valid JSON object, no extra text, no markdown.

            {{
            "question": "your question here?",
            "options": ["option a", "option b", "option c", "option d"],
            "correct_answer": "option a"
            }}

            rules:
            - correct_answer must exactly match one of the options
            - all 4 options must be different
            - question should be factual

            JSON:""",
            input_variables = ['difficulty','topic']
        )
    
        max_attempt=3
        last_error = None
        
        for attempt in range(max_attempt):
            try:
                response = self.chat_model.invoke(
                    prompt.format(topic=topic,difficulty=difficulty)
                )
                text = extract_text(response)
                data = extract_json(text)
                question = MCQQuestion(**data)
                
                if question.correct_answer not in question.options:
                    raise ValueError(f"Correct answer not in options list")
                return question 
            except Exception as e:
                last_error = e 
                continue 
        
        raise RuntimeError(f"could not generate MCQ after {max_attempt} tries , last error: {last_error}")
        
    ## *********** FillBlank method ***************************
    
    def generate_fill_blank(self,topic: str, difficulty:str = "medium") -> FillBlankQuestion:
        prompt = PromptTemplate(
            template = """Generate a {difficulty} difficulty fill in the blank question about: {topic}

Return ONLY a valid JSON object, no extra text, no markdown.

{{
  "question": "sentence with ______ as the blank",
  "answer": "correct word or phrase"
}}

rules:
- use exactly 6 underscores: ______
- answer should be specific and unambiguous
- blank should replace a key term

JSON:""",
            input_variables = ['difficulty','topic']
        )
        
        max_attempt = 3 
        last_error = None 
        
        for attempt in range(max_attempt):
            try:
                response = self.chat_model.invoke(
                    prompt.format(topic=topic, difficulty=difficulty)
                )
                text =extract_text(response)
                data = extract_json(text)
                question = FillBlankQuestion(**data)
                return question 
            except Exception as e:
                last_error = e
                continue 
        
        raise RuntimeError(f"Couldn't generate fill blank after {max_attempt} tries,last error: {last_error}")
                
        
        