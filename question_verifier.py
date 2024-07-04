from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env
load_dotenv()

class QuestionVerifier:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.9):
        self.llm = ChatOpenAI(model=model, temperature=temperature)

    def verify_question(self, question: str, answer: str, evaluation_criteria: str) -> str:
        """Verify the question and answer pair."""
        system_message = """You are an expert verifier at a business company responsible for ensuring the accuracy of question and answer pairs provided by users. Your task is to evaluate whether the answer given by the user correctly addresses the question according to the specified criteria.

        For each question and answer pair:
        - If the pair is correct, generate "True".
        - If the pair is incorrect, generate "Invalid Response, Suggestion:". Specify the correct answer suggestion based on the evaluation criteria.

        Examples:
        1. Correct Question and Answer Pair:
            Question: Ask Full Name of the User.
            User Answer: Rahul Kumar
            Evaluation Criteria: Every name should have a first name and a last name. The name should not contain any special characters or numbers.
            Your response: True

        2. Incorrect Question and Answer Pair:
            Question: Ask Full Name of the User.
            User Answer: Rahul
            Evaluation Criteria: Every name should have a first name and a last name. The name should not contain any special characters or numbers.
            Your response: Invalid Response, Suggestion: Please Enter Your Full Name. Example: John Doe, It should contain both first name and last name. No special characters or numbers are allowed.

        End of Example.
        """

        user_message_template = """
        Current Question: {question}
        User Answer: {answer}
        Evaluation Criteria: {evaluation_criteria}
        Evaluate the correctness of the question and answer pair based on the given criteria. Please respond with "True" or "Invalid Response, Suggestion:" based on the accuracy of the answer.
        """

        messages = [
            ("system", system_message),
            ("user", user_message_template.format(question=question, answer=answer, evaluation_criteria=evaluation_criteria))
        ]

        prompt_template = ChatPromptTemplate.from_messages(messages)
        prompt = prompt_template.invoke({})

        response = self.llm.invoke(prompt)
        response_text = response.content.strip()

        if response_text.startswith("True"):
            return True
        else:
            return response_text