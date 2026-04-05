from utils import QuestionGenerator

gen = QuestionGenerator()

print("Testing MCQ...")
mcq = gen.generate_mcq("Indian History", "medium")
print(f"Q: {mcq.question}")
print(f"Options: {mcq.options}")
print(f"Answer: {mcq.correct_answer}")

print("\nTesting Fill in the Blank...")
fib = gen.generate_fill_blank("Indian Geography", "easy")
print(f"Q: {fib.question}")
print(f"Answer: {fib.answer}")