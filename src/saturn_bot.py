from typing import Dict, List, Any
from utils.questions.question import questions_dic, evaluation_criteria_dic
from utils.role_config import config
from langchain.llms import BaseLLM
from pydantic import Field
from langchain.chains.base import Chain
from chain.conversation_chain import AgentConversationChain
from utils.question_verifier import QuestionVerifier
from repository import add_answer, get_user_questions_answered, update_user_questions_answered, create_user

question_verifier = QuestionVerifier()

class SaturnBot(Chain):
    conversation_history: List[str] = []
    conversation_chain: AgentConversationChain = Field(...)
    correct_responses: Dict[int, Any] = {}

    def get_question(self, question_no: int) -> str:
        return questions_dic.get(str(question_no))

    def get_question_id(self, question_no: int) -> str:
        question = self.get_question(question_no)
        return question.split(":")[0] if question else ""

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def generate_question(self, q_no: int) -> str:
        next_question = self.get_question(q_no)
        if next_question == '' or next_question == None:
            return "Conversation Ended"
        ai_message = self.conversation_chain.run(
            agent_name=config["agent_name"],
            agent_role=config["agent_role"],
            company_name=config["company_name"],
            company_business=config["company_business"],
            company_values=config["company_values"],
            conversation_history="\n".join(self.conversation_history),
            conversation_type=config["conversation_type"],
            next_question=next_question,
        )
        message = ai_message.split(":")[-1].rstrip("<END_OF_TURN>").strip()
        return message

    def add_ans_to_history(self, user_input: str):
        self.conversation_history.append(f"User: {user_input}<END_OF_TURN>")

    def add_question_to_history(self, question: str):
        self.conversation_history.append(f"{config['agent_name']}: {question}<END_OF_TURN>")

    def step(self, email: str, user_input: str) -> str:
        return self._call(email, user_input)

    def _call(self, email: str, user_input: str) -> str:
        current_question_no = get_user_questions_answered(email)
        print("\n".join(self.conversation_history))  # Debug: print conversation history
        question = self.get_question(current_question_no)
        if not question:
            return "Conversation Ended"

        evaluation_criteria = evaluation_criteria_dic.get(str(current_question_no))
        is_valid_response = question_verifier.verify_question(question, user_input, evaluation_criteria)

        if is_valid_response is True:
            add_answer(email, current_question_no, self.get_question_id(current_question_no), user_input)
            self.correct_responses[self.get_question_id(current_question_no)] = user_input
            if current_question_no == 0:
                create_user(email=email, full_name=user_input)
                add_answer(email, current_question_no, self.get_question_id(current_question_no), user_input)
                self.add_question_to_history(question)
            self.add_ans_to_history(user_input)
            generated_question = self.generate_question(current_question_no + 1)
            update_user_questions_answered(email, 1)
            self.add_question_to_history(generated_question)
            return generated_question

        return is_valid_response

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SaturnBot":
        conversation_chain = AgentConversationChain.from_llm(llm, verbose=verbose)
        return cls(conversation_chain=conversation_chain, verbose=verbose, **kwargs)