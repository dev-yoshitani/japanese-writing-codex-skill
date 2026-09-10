from dataclasses import dataclass, field


@dataclass(frozen=True)
class Sentence:
    id: int
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class Fact:
    kind: str
    value: str
    canonical: str
    start: int
    end: int

    @property
    def key(self):
        return self.kind, self.canonical


@dataclass(frozen=True)
class Alignment:
    source_ids: tuple[int, ...]
    target_ids: tuple[int, ...]
    confidence: float


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    source_ids: tuple[int, ...] = ()
    target_ids: tuple[int, ...] = ()
    details: dict = field(default_factory=dict)
