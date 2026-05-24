class LlmUpstreamError(Exception):
    """LLM provider returned an error or was unreachable."""
    pass


class LlmTimeoutError(LlmUpstreamError):
    """LLM call timed out."""
    pass


class LlmInvalidResponseError(Exception):
    """LLM returned a response that could not be parsed."""
    pass
