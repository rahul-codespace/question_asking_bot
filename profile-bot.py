from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import BaseLLM
from pydantic import Field, BaseModel
from langchain.chains.base import Chain
from langchain_openai import ChatOpenAI
from typing import Dict, List, Any
from questions import questions_dic, evaluation_criteria_dic
from role_config import config
from question_verifier import QuestionVerifier
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Load environment variables from .env
load_dotenv()

class AgentConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False):
        """Create the conversation chain with a given LLM and prompt."""
        prompt_template = """
        Never forget your name is {agent_name}.
        You work as a {agent_role}. You work at {company_name}.
        {company_name}'s business is the following: {company_business}.
        Your company values are {company_values}.
        You are currently in a conversation with a potential client.
        The purpose of this conversation is to collect information about the client's company.
        The conversation type is {conversation_type}.

        Keep your responses short to retain the user's attention. Never produce lists of questions. Always ask one question at a time.
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
            template=prompt_template,
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

class SaturnBot(Chain):
    conversation_history: List[str] = []
    current_question_no: str = "0"
    conversation_chain: AgentConversationChain = Field(...)
    question_responses: Dict[str, str] = {}

    def get_question(self, question_no: str) -> str:
        return questions_dic.get(question_no)

    def initialize_conversation(self, user_name: str):
        self.current_question_no = "1"
        self.conversation_history = [
            "Hello, this is Kedar Pandya from Saturn. May I have your name please?<END_OF_TURN>",
            f"User: {user_name}<END_OF_TURN>",
        ]

    def update_question_number(self):
        self.current_question_no = str(int(self.current_question_no) + 1)
        if self.current_question_no not in questions_dic:
            self.display_responses()

    def display_responses(self):
        print("Question Responses:")
        for question_no, response in self.question_responses.items():
            print(f"Question {question_no}: {response}")

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

# Initialize the bot and verifier
verbose = False
llm = ChatOpenAI(model="gpt-4", temperature=0.9)
saturn_bot = SaturnBot.from_llm(llm=llm, verbose=verbose)
question_verifier = QuestionVerifier()

class ConversationInput(BaseModel):
    input: str

@app.post("/api/bot/conversations/{user_name}")
async def start_conversation(user_name: str, inputDto: ConversationInput):
    if saturn_bot.current_question_no == "0":
        inputDto.input = user_name
    result = saturn_bot.step(inputDto.input)
    return {"message": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
