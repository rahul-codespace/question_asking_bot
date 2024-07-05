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


@app.post("/api/bot/conversations/{user_name}")
async def start_conversation(user_name: str, inputDto: ConversationInputDto):
    if saturn_bot.current_question_no == "0":
        inputDto.input = user_name
    result = saturn_bot.step(inputDto.input)
    return ConversationOutputDto(message=result, correct_responses=saturn_bot.correct_responses)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
