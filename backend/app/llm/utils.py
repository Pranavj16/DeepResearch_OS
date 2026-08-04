from time import perf_counter

from app.llm.models import ChatMessage, MessageRole


def extract_system_prompt(messages: list[ChatMessage]) -> str:
    """
    Extract the system prompt from a list of messages.

    Returns an empty string if no system message exists.
    """

    for message in messages:
        if message.role == MessageRole.SYSTEM:
            return message.content

    return ""


def extract_conversation(messages: list[ChatMessage]) -> list[ChatMessage]:
    """
    Return all non-system messages.

    Useful for providers that send the system prompt separately.
    """

    return [message for message in messages if message.role != MessageRole.SYSTEM]


def join_message_contents(messages: list[ChatMessage]) -> str:
    """
    Join message contents into a single string.

    Used by providers that expect one prompt string.
    """

    return "\n\n".join(message.content for message in messages)


class Timer:
    """
    Simple timer for measuring request latency.
    """

    def __init__(self) -> None:
        self.start = perf_counter()

    @property
    def elapsed_ms(self) -> float:
        """
        Return elapsed time in milliseconds.
        """

        return round(
            (perf_counter() - self.start) * 1000,
            2,
        )
