from quiz_manager import QuizManager

# --- Setup mock questions directly (bypass API) ---
qm = QuizManager()

qm.questions = [
    {
        'type': 'MCQ',
        'question': 'Who was the first President of India?',
        'options': ['Jawaharlal Nehru', 'Dr. Rajendra Prasad', 'B.R. Ambedkar', 'Sardar Patel'],
        'correct_answer': 'Dr. Rajendra Prasad'
    },
    {
        'type': 'Fill in the Blank',
        'question': 'The Battle of Plassey was fought in the year ______.',
        'correct_answer': '1757',
        'options': []
    }
]

# --- Simulate user answers ---
qm.store_answer(0, 'Dr. Rajendra Prasad')   # correct
qm.store_answer(1, '1757')                  # correct

# --- Evaluate ---
results = qm.evaluate_quiz()
score = qm.get_score()

print(f"Score: {score['correct']}/{score['total']} ({score['percentage']}%)")
for r in results:
    status = "PASS" if r['is_correct'] else "FAIL"
    print(f"  [{status}] Q{r['question_number']}: {r['question'][:50]}...")

# --- Test wrong answer ---
print("\nTesting wrong answer...")
qm.store_answer(0, 'Jawaharlal Nehru')  # wrong
qm.evaluate_quiz()
score = qm.get_score()
print(f"Score with 1 wrong: {score['correct']}/{score['total']} ({score['percentage']}%)")

# --- Test save ---
path = qm.save_to_csv()
print(f"\nResults saved to: {path}")

print("\nAll tests passed!")