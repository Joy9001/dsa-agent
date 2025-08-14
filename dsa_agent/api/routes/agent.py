from enum import StrEnum

from agent.dsa_agent import DSAAgent
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from logger import logger
from pydantic import BaseModel

agent_router = APIRouter(prefix="/agents", tags=["Agents"])


class Model(StrEnum):
    gemini_2_5_flash = "gemini-2.5-flash"
    gemini_2_5_pro = "gemini-2.5-pro"


class RunRequest(BaseModel):
    """Request model for running the agent"""

    message: str
    stream: bool = True
    model: Model = Model.gemini_2_5_flash
    user_id: str | None = None
    session_id: str | None = None


@agent_router.post("/run", status_code=status.HTTP_200_OK)
async def create_agent_run(body: RunRequest):
    """
    Sends a message to a specific agent and returns the response.

    Args:
        body: Request parameters including the message

    Returns:
        Either a streaming response or the complete agent response
    """
    logger.debug(f"RunRequest: {body}")

    try:
        agent = DSAAgent(body.user_id, body.session_id, body.model.value)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if body.stream:
        return StreamingResponse(
            agent.astream_agent(msg=body.message),
            media_type="text/event-stream",
        )
    else:
        response = await agent.arun_agent(msg=body.message)
        return response
