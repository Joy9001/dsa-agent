import json
import uuid
from enum import StrEnum
from typing import AsyncGenerator

from agent.agent import DSAAgent
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from logger import logger
from pydantic import BaseModel

from utils.gen_userid import generate_user_id

agent_router = APIRouter(prefix="/agents", tags=["Agents"])


async def stream_json_response(
    agent_stream: AsyncGenerator,
) -> AsyncGenerator[str, None]:
    """Convert agent dictionary responses to JSON strings for streaming"""
    async for content in agent_stream:
        if isinstance(content, dict):
            yield json.dumps(content) + "\n"
        else:
            yield str(content) + "\n"


class Model(StrEnum):
    gemini_2_5_flash = "gemini-2.5-flash"
    gemini_2_5_pro = "gemini-2.5-pro"


class RunRequest(BaseModel):
    """Request model for running the agent"""

    message: str
    stream: bool = True
    model: Model = Model.gemini_2_5_flash
    session_id: str | None = None
    debug_mode: bool = True
    lc_site: str = "global"
    lc_session: str
    gh_token: str
    gemini_api_key: str


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
        config = {"lc_session": body.lc_session, "gh_token": body.gh_token}
        user_id = generate_user_id(config)
        session_id = body.session_id or str(uuid.uuid4())
        agent = DSAAgent(
            user_id=user_id,
            session_id=session_id,
            model_id=body.model.value,
            debug_mode=body.debug_mode,
            lc_site=body.lc_site,
            lc_session=body.lc_session,
            gh_token=body.gh_token,
            gemini_api_key=body.gemini_api_key,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if body.stream:
        return StreamingResponse(
            stream_json_response(agent.astream_agent(msg=body.message)),
            media_type="text/event-stream",
        )
    else:
        response = await agent.arun_agent(msg=body.message)
        return {"response": response, "session_id": session_id, "user_id": user_id}
