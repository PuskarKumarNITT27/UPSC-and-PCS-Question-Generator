import os 
import pandas as pd 
from datetime import datetime
from utils import QuestionGenerator


############## Quiz Manager ###########################

class QuizManager: 
    
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []
    
    def reset(self):
        self.questions = []
        self.user_answers = []
        self.results = []
    
    def generate_questions(self,topic: str, question_type: str,difficulty:str, num_questions:int) -> bool:
        self.reset()
        
        if not topic.strip():
            raise ValueError("topic can't be empty")
        
        generator = QuestionGenerator()
        
        for i in range(num_questions):
            if question_type == "Multiple Choice":
                q = generator.generate_mcq(topic=topic,difficulty=difficulty.lower())
                self.questions.append({
                    'type':'MCQ',
                    'question':q.question,
                    'options':q.options,
                    'correct_answer':q.correct_answer
                })
            else: 
                q= generator.generate_fill_blank(topic=topic,difficulty=difficulty.lower())
                self.questions.append({
                    'type':'Fill in the Blanks',
                    'question':q.question,
                    'correct_answer':q.answer,
                    'options':[]
                })
        return True 
    
    def store_answer(self,index:int,answer:str):
        while len(self.user_answers) <= index:
            self.user_answers.append("")
        self.user_answers[index] = answer
        
    def evaluate_quiz(self) -> list: 
        
        if not self.questions:
            raise ValueError("no question to evaluate")

        if len(self.user_answers) != len(self.questions):
            raise ValueError("answer couldn't match question count")

        self.results = []
        
        for i,(q,ans) in enumerate(zip(self.questions,self.user_answers)):
            if q['type'] == 'MCQ':
                is_correct = ans == q['correct_answer']
            else:
                is_correct = ans.strip().lower() == q['correct_answer'].strip().lower()
            
            self.results.append({
                'question_number':i+1,
                'question_type':q['type'],
                'question':q['question'],
                'options':q.get('options',[]),
                'user_answer':ans,
                'correct_answer':q['correct_answer'],
                'is_correct':is_correct
            })
        return self.results

    
    def get_score(self) -> dict:
        
        if not self.results:
            raise ValueError("no results yet, run evaluate quiz first")
        
        correct = sum(1 for r in self.results if r['is_correct'])
        
        total = len(self.results)
        percentage = (correct/total)*100 
        
        return {
            'correct':correct,
            'total':total,
            'percentage':round(percentage,2)
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        
        if not self.results:
            return pd.DataFrame
        return pd.DataFrame(self.results)

    def save_to_csv(self) -> str: 
        
        if not self.results:
            raise ValueError('No results to save')
        
        df = self.to_dataframe()
        
        os.makedirs('results',exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('results',f"quiz_results_{timestamp}.csv")
        
        df.to_csv(filepath,index=False)
        return filepath