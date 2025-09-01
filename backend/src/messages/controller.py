from datetime import datetime
from .schema import MessageInput, MessageResponse, CacheInfo, ProcessingInfo


class MessageController:
    def __init__(self):
        pass

    def get_info(self):
        return {
            "status": "ok",
            "message": "Message API is running",
            "timestamp": datetime.now(),
        }

    def create_message(self, message: MessageInput) -> MessageResponse:
        cache_info = None
        processing_info = None
        if message.get_cache_info:
            cache_info = CacheInfo(hit=False, cache_timestamp=None, num_hits=0)
        if message.get_processing_info:
            processing_info = ProcessingInfo(
                start_timestamp=datetime.now(), end_timestamp=datetime.now()
            )

        return MessageResponse(
            message=message.message,
            cache_info=cache_info,
            processing_info=processing_info,
        )


message_controller = MessageController()
