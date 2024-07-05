from typing import Dict, List, Any
from utils.questions.question import questions_dic, evaluation_criteria_dic
from utils.role_config import config
from langchain.llms import BaseLLM
from pydantic import Field
from langchain.chains.base import Chain
from chain.conversation_chain import AgentConversationChain
from utils.question_verifier import QuestionVerifier

question_verifier = QuestionVerifier()

class SaturnBot(Chain):
    conversation_history: List[str] = []
    current_question_no: str = "0"
    conversation_chain: AgentConversationChain = Field(...)
    correct_responses: Dict[str, Any] = {}

    def get_question(self, question_no: str) -> str:
        return questions_dic.get(question_no)

    def get_question_id(self, question_no: str) -> str:
        return questions_dic.get(question_no).split(":")[0]

    def update_question_number(self):
        self.current_question_no = str(int(self.current_question_no) + 1)

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def step(self, user_input: str) -> str:
        return self._call(user_input)

    def generate_question(self):
        next_question = self.get_question(self.current_question_no)
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
        return ai_message.split(':', 1)[-1].strip().rstrip('<END_OF_TURN>')

    def add_to_history(self, user_input: str, question: str):
        self.conversation_history.append(f"User: {user_input}<END_OF_TURN>")
        self.conversation_history.append(f"{config['agent_name']}: {question}<END_OF_TURN>")

    def add_question_to_history(self, question: str):
        self.conversation_history.append(f"{config['agent_name']}: {question}<END_OF_TURN>")

    def _call(self, user_input: str) -> str:
        # print the conversation history
        print("\n".join(self.conversation_history))
        question = self.get_question(self.current_question_no)
        if not question:
            return "Conversation Ended"

        evaluation_criteria = evaluation_criteria_dic.get(self.current_question_no)
        is_valid_response = question_verifier.verify_question(question, user_input, evaluation_criteria)

        if is_valid_response is True:
            self.correct_responses[self.get_question_id(self.current_question_no)] = user_input
            if self.current_question_no == "0":
                self.update_question_number()
                generated_question = self.generate_question()
                self.add_question_to_history(question) # Add the system message to the conversation history
                self.add_to_history(user_input, generated_question) # Add the user input and generated question to the conversation history
                return generated_question

            self.update_question_number()

            generated_question = self.generate_question()
            self.add_to_history(user_input, generated_question) # Add the user input and generated question to the conversation history
            return generated_question

        return is_valid_response

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SaturnBot":
        conversation_chain = AgentConversationChain.from_llm(llm, verbose=verbose)
        return cls(conversation_chain=conversation_chain, verbose=verbose, **kwargs)