from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env
load_dotenv()

class QuestionVerifier:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.9):
        self.llm = ChatOpenAI(model=model, temperature=temperature)

    def verify_question(self, question: str, answer: str, evaluation_criteria: str) -> bool:
        """Verify the question and answer pair"""
        messages = [
            ("system", """You are an expert verifier at a business company responsible for ensuring the accuracy of question and answer pairs provided by users. Your task is to evaluate whether the answer given by the user correctly addresses the question according to the specified criteria.

                For each question and answer pair:
                - If the pair is correct, generate "True".
                - If the pair is incorrect, generate "False".

                Example:
                    Question: What is your full name?
                    User Answer: Rahul Kumar
                    Evaluation Criteria: [Every name should have a first name and a last name. The name should not contain any special characters or numbers.]
                    Your response: True
                End of Example.
                """),
            ("user", """
                Current Question: {question}
                User Answer: {answer}
                Evaluation Criteria: {evaluation_criteria}
                Evaluate the correctness of the question and answer pair based on the given criteria. Please respond with "True" or "False" based on the accuracy of the answer.
                """
            )
        ]
        prompt_templete = ChatPromptTemplate.from_messages(messages)
        prompt = prompt_templete.invoke({"question": question, "answer": answer, "evaluation_criteria": evaluation_criteria})
        response = self.llm.invoke(prompt)
        return response.content == "True"