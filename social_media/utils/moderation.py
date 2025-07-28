import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class ContentModerator:
    def __init__(self) -> None:
        """Initialize the ContentModerator with OpenAI client."""
        if not settings.OPENAI_MODERATION_API_KEY:
            msg = "OpenAI Moderation API key is not configured"
            raise ValueError(msg)
        self.openai: OpenAI = OpenAI(
            api_key=settings.OPENAI_MODERATION_API_KEY,
        )

    def is_potentially_harmful(self, content: str) -> bool:
        logger.info(f"Checking content for harmfulness: {content[:50]}...")  # noqa: G004
        try:
            response = self.openai.moderations.create(
                input=content,
            )
            return response.results[0].flagged
        except Exception as e:
            logger.exception("Error checking content for harmfulness: %s", e)  # noqa: TRY401
            return False
