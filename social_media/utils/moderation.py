import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class ContentModerator:
    """
    ContentModerator provides functionality to check if a given text content is potentially harmful
    using the OpenAI Moderation API.
    Attributes:
        openai (OpenAI): An instance of the OpenAI client initialized with the moderation API key.
    Methods:
        __init__():
            Initializes the ContentModerator with the OpenAI Moderation API key from settings.
            Raises ValueError if the API key is not configured.
        is_potentially_harmful(content: str) -> bool:
            Checks if the provided content is flagged as potentially harmful by the OpenAI Moderation API.
            Logs the check and handles exceptions gracefully.
            Returns True if the content is flagged as harmful, otherwise False.
    """  # noqa: E501

    def __init__(self) -> None:
        """Initialize the ContentModerator with OpenAI client."""
        if not settings.OPENAI_MODERATION_API_KEY:
            msg = "OpenAI Moderation API key is not configured"
            raise ValueError(msg)
        self.openai: OpenAI = OpenAI(
            api_key=settings.OPENAI_MODERATION_API_KEY,
        )

    def is_potentially_harmful(self, content: str) -> bool:
        """
        Checks if the provided content is potentially harmful using OpenAI's moderation API.
        Args:
            content (str): The text content to be evaluated for harmfulness.
        Returns:
            bool: True if the content is flagged as potentially harmful, False otherwise.
        """  # noqa: E501

        logger.info(f"Checking content for harmfulness: {content[:50]}...")  # noqa: G004
        try:
            response = self.openai.moderations.create(
                input=content,
            )
            return response.results[0].flagged
        except Exception as e:
            logger.exception("Error checking content for harmfulness: %s", e)  # noqa: TRY401
            return False
