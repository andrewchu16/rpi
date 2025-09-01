from fastapi import APIRouter
from .schema import MessageInput, MessageResponse
from .controller import message_controller

router = APIRouter()


@router.post("/response", response_model=MessageResponse)
async def get_response(message: MessageInput):
    return message_controller.create_message(message)


@router.get("/info")
async def get_info():
    return message_controller.get_info()
