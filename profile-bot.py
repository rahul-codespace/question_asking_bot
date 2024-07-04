from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import BaseLLM
from pydantic import Field
from langchain.chains.base import Chain
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
from questions import questions_dic, evaluation_criteria_dic
from role_config import config
from question_verifier import QuestionVerifier
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Load environment variables from .env
load_dotenv()

class SaturnAgentConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False):
        """Get the response parser"""
        saturn_agent_inception_prompt = """
        Never forget your name is {agent_name}.
        You work as a {agent_role}. You work at {company_name}.
        {company_name}'s business is the following: {company_business}.
        Your company values are {company_values}.
        You are currently in a conversation with a potential client.
        The purpose of this conversation is to collect information about the client's company.
        The conversation type is {conversation_type}.

        Keep your responses in short length to retain the user's attention. Never produce lists of questions. Always ask one question at a time.
        You must respond according to the previous conversation history. Only ask one question at a time! When you are done with generating the question, please add <END_OF_TURN> at the end of the question to give the user a chance to respond.

        Example:
        Conversation History:
        Hello there! This is {agent_name} from {company_name}. Before we get started, could you please tell me your full name?
        User: Sure! My name is John Doe. <END_OF_TURN>
        End of Example.

        Current Conversation:
        Conversation history: {conversation_history}
        Next Question: {next_question}
        """

        prompt = PromptTemplate(
            template=saturn_agent_inception_prompt,
            input_variables=[
                "agent_name",
                "agent_role",
                "company_name",
                "company_business",
                "company_values",
                "conversation_history",
                "conversation_type",
                "next_question",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)

class SaturnGPT(Chain):
    conversation_history: List[str] = []
    current_question_no: str = "0"
    saturn_agent_conversation_chain: SaturnAgentConversationChain = Field(...)
    question_responses: Dict[str, str] = {}

    def retrieve_question(self, question_no: str) -> str:
        return questions_dic.get(question_no)

    def seed_agent(self, user_name: str):
        self.current_question_no = "1"
        self.conversation_history = [
            "Hello, this is Kedar Pandya from Saturn. May I have your name please?<END_OF_TURN>",
            f"User: {user_name}<END_OF_TURN>",
        ]

    def get_conversation_history(self):
        return self.conversation_history

    def determine_next_question_no(self):
        self.current_question_no = str(int(self.current_question_no) + 1)
        if self.current_question_no not in questions_dic:
            self.print_question_responses()

    def print_question_responses(self):
        print("Question Responses:")
        for question_no, response in self.question_responses.items():
            print(f"Question {question_no}: {response}")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def step(self, user_input: str)-> str:
        return self._call(user_input)

    def generateQuestion(self):
        next_question = self.retrieve_question(self.current_question_no)
        ai_message = self.saturn_agent_conversation_chain.run(
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

    def add_conversation_history(self, question: str, user_input: str):
        self.conversation_history.append(f"{config['agent_name']}: {question}<END_OF_TURN>")
        self.conversation_history.append(f"User: {user_input}<END_OF_TURN>")


    def _call(self, user_input: str) -> str:
        # check user input is correct or not
        question = questions_dic.get(self.current_question_no)
        if question is None:
            return "Conversation Ended"
        evaluation_criteria = evaluation_criteria_dic.get(self.current_question_no)
        is_valid_response = question_verifier.verify_question(question, user_input, evaluation_criteria)
        if is_valid_response is True:
            if self.current_question_no == "0":
                self.add_conversation_history(question, user_input)
                self.determine_next_question_no()
                generated_question = self.generateQuestion()
                self.conversation_history.append(f"{config['agent_name']}: {generated_question}<END_OF_TURN>")
                return generated_question
            self.determine_next_question_no()
            privious_ai_generated_question = self.conversation_history[-1].split(':')[1].strip().rstrip('<END_OF_TURN>')
            self.add_conversation_history(privious_ai_generated_question, user_input)
            generated_question = self.generateQuestion()
            self.conversation_history.append(f"{config['agent_name']}: {generated_question}<END_OF_TURN>")
            return generated_question
        else:
            return is_valid_response

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SaturnGPT":
        saturn_agent_conversation_chain = SaturnAgentConversationChain.from_llm(llm, verbose=verbose)
        return cls(saturn_agent_conversation_chain=saturn_agent_conversation_chain, verbose=verbose, **kwargs)

# Initialize your agent and verifier
verbose = False
llm = ChatOpenAI(model="gpt-4o", temperature=0.9)
sales_agent = SaturnGPT.from_llm(llm=llm, verbose=verbose)
question_verifier = QuestionVerifier()

class ConversationInput(BaseModel):
    input: str

@app.post("/api/bot/conversations/{user_name}")
async def start_conversation(user_name, inputDto: ConversationInput):
    if sales_agent.current_question_no == "0":
        inputDto.input = user_name
    result = sales_agent.step(inputDto.input)
    return {"message": result}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)