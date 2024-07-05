from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from models.model import ConversationInputDto, ConversationOutputDto
from saturn_bot import SaturnBot
from fastapi import FastAPI
import uvicorn

app = FastAPI()

load_dotenv()

verbose = False
llm = ChatOpenAI(model="gpt-4", temperature=0.9)
saturn_bot = SaturnBot.from_llm(llm=llm, verbose=verbose)


@app.post("/api/bot/conversations/{email}")
async def start_conversation(email: str, inputDto: ConversationInputDto):
    result = saturn_bot.step(email=email, user_input=inputDto.message)
    return ConversationOutputDto(message=result, correct_responses=saturn_bot.correct_responses)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
