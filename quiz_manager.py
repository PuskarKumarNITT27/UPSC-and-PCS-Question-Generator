import os
import pandas as pd
from datetime import datetime
from utils import QuestionGenerator


class QuizManager:

    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []

    def reset(self):
        """Clear all quiz state — call before generating a new quiz."""
        self.questions = []
        self.user_answers = []
        self.results = []

    def generate_questions(
        self,
        topic: str,
        question_type: str,
        difficulty: str,
        num_questions: int
    ) -> bool:
        """
        Generate questions and store them internally.
        Returns True on success, False on failure.
        """
        self.reset()

        if not topic.strip():
            raise ValueError("Topic cannot be empty. Please enter a topic.")

        generator = QuestionGenerator()

        for i in range(num_questions):
            if question_type == "Multiple Choice":
                question = generator.generate_mcq(topic, difficulty.lower())
                self.questions.append({
                    'type': 'MCQ',
                    'question': question.question,
                    'options': question.options,
                    'correct_answer': question.correct_answer
                })
            else:
                question = generator.generate_fill_blank(topic, difficulty.lower())
                self.questions.append({
                    'type': 'Fill in the Blank',
                    'question': question.question,
                    'correct_answer': question.answer,
                    'options': []
                })

        return True

    def store_answer(self, question_index: int, answer: str):
        """Store a single user answer by question index."""
        # Ensure list is long enough
        while len(self.user_answers) <= question_index:
            self.user_answers.append("")
        self.user_answers[question_index] = answer

    def evaluate_quiz(self) -> list:
        """
        Evaluate all answers against correct answers.
        Returns list of result dicts.
        """
        if not self.questions:
            raise ValueError("No questions to evaluate.")
        if len(self.user_answers) != len(self.questions):
            raise ValueError("Answer count doesn't match question count.")

        self.results = []

        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            if q['type'] == 'MCQ':
                is_correct = user_ans == q['correct_answer']
            else:
                # Case-insensitive strip comparison for fill in the blank
                is_correct = user_ans.strip().lower() == q['correct_answer'].strip().lower()

            self.results.append({
                'question_number': i + 1,
                'question_type': q['type'],
                'question': q['question'],
                'options': q.get('options', []),
                'user_answer': user_ans,
                'correct_answer': q['correct_answer'],
                'is_correct': is_correct
            })

        return self.results

    def get_score(self) -> dict:
        """
        Returns score summary dict.
        Call after evaluate_quiz().
        """
        if not self.results:
            raise ValueError("No results yet. Run evaluate_quiz() first.")

        correct = sum(1 for r in self.results if r['is_correct'])
        total = len(self.results)
        percentage = (correct / total) * 100

        return {
            'correct': correct,
            'total': total,
            'percentage': round(percentage, 1)
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to a pandas DataFrame."""
        if not self.results:
            return pd.DataFrame()
        return pd.DataFrame(self.results)

    def save_to_csv(self) -> str:
        """
        Save results to a timestamped CSV in the results/ folder.
        Returns the saved file path.
        """
        if not self.results:
            raise ValueError("No results to save.")

        df = self.to_dataframe()
        os.makedirs('results', exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join('results', f"quiz_results_{timestamp}.csv")
        df.to_csv(filepath, index=False)

        return filepath