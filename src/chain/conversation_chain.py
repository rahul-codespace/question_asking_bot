from langchain.llms import BaseLLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Define the AgentConversationChain class
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

        Keep your responses short to retain the user's attention. Never produce lists of questions. Always ask one question at a time from agent side.
        You must respond according to the previous conversation history. Only ask one question at a time! When you are done with generating the question, please add <END_OF_TURN> at the end of the question to give the user a chance to respond.

        Example:
        Conversation History:
        Hello there! This is {agent_name} from {company_name}. Before we get started, could you please tell me your full name?<END_OF_TURN>
        User: Sure! My name is John Doe.<END_OF_TURN>
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