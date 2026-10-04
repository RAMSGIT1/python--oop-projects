import csv
import datetime
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class QuestionLoadError(Exception):
    """Raised when there is an issue reading or parsing questions."""

    pass


class InvalidAnswerError(Exception):
    """Raised when the submitted answer format is invalid."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Question(ABC):
    """Abstract base class representing a generic quiz question."""

    def __init__(self, prompt: str):
        self._prompt = prompt  # Protected attribute

    @property
    def prompt(self) -> str:
        return self._prompt

    @abstractmethod
    def display(self, question_number: int):
        """Displays question prompt and answer options."""
        pass

    @abstractmethod
    def check_answer(self, user_answer: str) -> bool:
        """Evaluates whether the user's answer matches the correct one."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class MCQQuestion(Question):
    """Multiple Choice Question with 4 selectable options (A, B, C, D)."""

    def __init__(self, prompt: str, options: list[str], correct_option: str):
        super().__init__(prompt)
        if len(options) != 4:
            raise QuestionLoadError("MCQ must contain exactly 4 options.")
        self._options = options
        self.__correct_option = correct_option.strip().upper()

    @property
    def options(self) -> list[str]:
        return self._options

    def display(self, question_number: int):
        print(f"\nQ{question_number}: {self.prompt}")
        labels = ["A", "B", "C", "D"]
        for label, opt in zip(labels, self._options):
            print(f"  [{label}] {opt}")

    def check_answer(self, user_answer: str) -> bool:
        cleaned = user_answer.strip().upper()
        if cleaned not in ["A", "B", "C", "D"]:
            raise InvalidAnswerError("Please enter A, B, C, or D.")
        return cleaned == self.__correct_option


class TrueFalseQuestion(Question):
    """Binary True or False Question."""

    def __init__(self, prompt: str, correct_answer: bool):
        super().__init__(prompt)
        self.__correct_answer = correct_answer

    def display(self, question_number: int):
        print(f"\nQ{question_number}: {self.prompt}")
        print("  [T] True")
        print("  [F] False")

    def check_answer(self, user_answer: str) -> bool:
        cleaned = user_answer.strip().upper()
        if cleaned not in ["T", "F", "TRUE", "FALSE"]:
            raise InvalidAnswerError("Please enter 'T' or 'F'.")
        selected = cleaned in ["T", "TRUE"]
        return selected == self.__correct_answer


# ==========================================
# 4. Management Class: QuizManager
# ==========================================
class QuizManager:
    """Loads questions, conducts quizzes, grades, and records scores."""

    def __init__(
        self,
        questions_file: str = "questions.csv",
        results_file: str = "quiz_results.csv",
    ):
        self.questions_file = questions_file
        self.results_file = results_file
        self.questions: list[Question] = []
        self.load_questions()

    def load_questions(self):
        self.questions.clear()
        if not os.path.exists(self.questions_file):
            return

        try:
            with open(
                self.questions_file, mode="r", newline="", encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q_type = row["type"].strip().upper()
                    prompt = row["prompt"].strip()

                    if q_type == "MCQ":
                        options = [
                            row["opt_a"].strip(),
                            row["opt_b"].strip(),
                            row["opt_c"].strip(),
                            row["opt_d"].strip(),
                        ]
                        correct = row["correct"].strip()
                        self.questions.append(
                            MCQQuestion(prompt, options, correct)
                        )
                    elif q_type == "TF":
                        correct_bool = row["correct"].strip().lower() in [
                            "true",
                            "t",
                            "1",
                        ]
                        self.questions.append(
                            TrueFalseQuestion(prompt, correct_bool)
                        )
        except Exception as e:
            raise QuestionLoadError(f"Error parsing '{self.questions_file}': {e}")

    def add_mcq_question(
        self, prompt: str, options: list[str], correct_option: str
    ):
        q = MCQQuestion(prompt, options, correct_option)
        self.questions.append(q)
        self._append_question_to_csv(
            "MCQ", prompt, options, correct_option.upper()
        )
        print("✓ MCQ question added successfully.")

    def add_tf_question(self, prompt: str, correct_val: bool):
        q = TrueFalseQuestion(prompt, correct_val)
        self.questions.append(q)
        self._append_question_to_csv(
            "TF", prompt, ["", "", "", ""], str(correct_val)
        )
        print("✓ True/False question added successfully.")

    def _append_question_to_csv(
        self, q_type: str, prompt: str, opts: list[str], correct: str
    ):
        file_exists = os.path.exists(self.questions_file)
        with open(
            self.questions_file, mode="a", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(self.questions_file) == 0:
                writer.writerow(
                    ["type", "prompt", "opt_a", "opt_b", "opt_c", "opt_d", "correct"]
                )
            writer.writerow(
                [q_type, prompt, opts[0], opts[1], opts[2], opts[3], correct]
            )

    def conduct_quiz(self, candidate_name: str) -> float:
        if not self.questions:
            print("Question bank is empty. Add questions before taking the quiz.")
            return 0.0

        score = 0
        total = len(self.questions)
        print("\n" + "=" * 60)
        print(f"STARTING QUIZ FOR: {candidate_name.upper()}".center(60))
        print("=" * 60)

        for idx, q in enumerate(self.questions, start=1):
            q.display(idx)
            while True:
                user_ans = input("Your answer: ").strip()
                try:
                    if q.check_answer(user_ans):
                        score += 1
                        print("✓ Correct!")
                    else:
                        print("✗ Incorrect.")
                    break
                except InvalidAnswerError as err:
                    print(f"  Invalid format: {err} Please try again.")

        percentage = round((score / total) * 100, 2)
        print("\n" + "-" * 60)
        print(f"Quiz Completed! Final Score: {score}/{total} ({percentage}%)")
        print("-" * 60)

        self._save_result(candidate_name, score, total, percentage)
        return percentage

    def _save_result(
        self, candidate_name: str, score: int, total: int, percentage: float
    ):
        file_exists = os.path.exists(self.results_file)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(
                self.results_file, mode="a", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                if not file_exists or os.path.getsize(self.results_file) == 0:
                    writer.writerow(
                        ["timestamp", "candidate_name", "score", "total", "percentage"]
                    )
                writer.writerow(
                    [timestamp, candidate_name, score, total, percentage]
                )
            print(f"✓ Result successfully saved to '{self.results_file}'.")
        except IOError as e:
            print(f"Error saving quiz result: {e}")

    def display_results(self):
        if not os.path.exists(self.results_file):
            print("No saved results found.")
            return

        print("\n" + "=" * 70)
        print("CANDIDATE PERFORMANCE RECORDS".center(70))
        print("=" * 70)
        with open(
            self.results_file, mode="r", newline="", encoding="utf-8"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(
                    f"{row['timestamp']} | Candidate: {row['candidate_name']:<15} | "
                    f"Score: {row['score']}/{row['total']} ({row['percentage']}%)"
                )
        print("=" * 70)


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = QuizManager()

    while True:
        print("\n=== QUIZ MANAGEMENT SYSTEM ===")
        print("1. Take Quiz")
        print("2. Add Multiple Choice Question (MCQ)")
        print("3. Add True / False Question")
        print("4. View All Quiz Results")
        print("5. Exit")

        choice = input("Enter choice (1-5): ").strip()

        try:
            if choice == "1":
                name = input("Enter Candidate Name: ").strip()
                if not name:
                    print("Candidate name cannot be empty.")
                    continue
                manager.conduct_quiz(name)

            elif choice == "2":
                prompt = input("Enter question prompt: ").strip()
                a = input("Option A: ").strip()
                b = input("Option B: ").strip()
                c = input("Option C: ").strip()
                d = input("Option D: ").strip()
                ans = input("Correct Option (A/B/C/D): ").strip().upper()
                if ans not in ["A", "B", "C", "D"]:
                    print("Invalid correct option! Must be A, B, C, or D.")
                    continue
                manager.add_mcq_question(prompt, [a, b, c, d], ans)

            elif choice == "3":
                prompt = input("Enter statement prompt: ").strip()
                ans_str = input("Is statement True or False? (T/F): ").strip().upper()
                if ans_str not in ["T", "F"]:
                    print("Invalid input. Must be T or F.")
                    continue
                manager.add_tf_question(prompt, ans_str == "T")

            elif choice == "4":
                manager.display_results()

            elif choice == "5":
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid selection. Please choose from 1 to 5.")

        except QuestionLoadError as qe:
            print(f"Data Load Error: {qe}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()