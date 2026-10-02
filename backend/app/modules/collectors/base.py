from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CollectedItem:
    title: str
    content: str
    url: str
    published_at: datetime | None


class Collector(ABC):
    """Interface commune a tous les collecteurs (/data/collectors).

    Chaque source (RSS, API institutionnelle, page corporate...) implemente
    cette interface, ce qui permet d'ajouter de nouveaux types de sources sans
    toucher au pipeline de traitement en aval.
    """

    @abstractmethod
    def collect(self) -> list[CollectedItem]:
        raise NotImplementedError
