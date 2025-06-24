from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from agent_service import query_agent
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Add this before defining your endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    try:
        answer = query_agent(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))