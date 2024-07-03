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

verbose = False
llm = ChatOpenAI(model="gpt-4o", temperature=0.9)

class SaturnGPT(Chain):
    conversation_history: List[str] = []
    current_question_no: str = "1"
    saturn_agent_conversation_chain: SaturnAgentConversationChain = Field(...)
    question_responses: Dict[str, str] = {}

    def retrieve_question(self, question_no: str) -> str:
        return questions_dic.get(question_no, "1")

    def seed_agent(self):
        self.current_question_no = "1"
        self.conversation_history = config["conversation_history"]

    def get_current_question_no(self):
        return self.current_question_no

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

    def step(self):
        self._call(inputs={})

    def _call(self, inputs: Dict[str, Any]) -> None:
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

        # Store the question response
        self.question_responses[self.current_question_no] = self.conversation_history[-1].split(":")[-1].strip().replace("<END_OF_TURN>", "")

        self.conversation_history.append(f"{config['agent_name']}: {ai_message}")

        print(f"Current Question No {self.current_question_no}: {questions_dic.get(self.current_question_no, '1')}")
        print("****************************************************************************************************")
        print(f"{config['agent_name']}: {ai_message.split(':', 1)[-1].strip().rstrip('<END_OF_TURN>')}")

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SaturnGPT":
        saturn_agent_conversation_chain = SaturnAgentConversationChain.from_llm(llm, verbose=verbose)
        return cls(saturn_agent_conversation_chain=saturn_agent_conversation_chain, verbose=verbose, **kwargs)

# Initialize your agent
sales_agent = SaturnGPT.from_llm(llm=llm, verbose=verbose)

# Seed the agent with initial conversation history
sales_agent.seed_agent()
#  Initialize the QuestionVerifier
question_verifier = QuestionVerifier()

# Start the interaction loop
while True:
    sales_agent.step()
    user_input = input("User: ")
    print("\n\n")
    if user_input.lower() == "exit":
        sales_agent.print_question_responses()
        break
    while True:
        evaluation_criteria = evaluation_criteria_dic.get(sales_agent.get_current_question_no(), "1")
        question = questions_dic.get(sales_agent.get_current_question_no(), "1")
        if question_verifier.verify_question(question, user_input, evaluation_criteria):
            break
        else:
            print("Please provide a valid response.")
            user_input = input("User: ")
            print("\n\n")
    sales_agent.conversation_history.append(f"User: {user_input}<END_OF_TURN>")
    sales_agent.determine_next_question_no()