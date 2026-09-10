"""Model-neutral interfaces; providers remain optional, explicitly supplied code."""
import copy
from typing import Protocol


class Adapter(Protocol):
    def propose(self, request: dict) -> dict: ...


class CallableAdapter:
    """Wrap a caller-supplied OpenAI, Claude or local-model function.

    The function receives trusted instruction and untrusted document data as
    separate fields. It must preserve this boundary in its provider's request.
    No provider is contacted by this library itself.
    """
    def __init__(self, function):
        self.function = function

    def propose(self, request):
        return self.function(copy.deepcopy(request))


class ReplayAdapter:
    """Explicit in-memory responses; never records user text automatically."""
    def __init__(self, responses):
        self.responses = iter(copy.deepcopy(responses))

    def propose(self, request):
        try:
            return next(self.responses)
        except StopIteration:
            raise ValueError("Replay responses exhausted") from None
