from pydantic import BaseModel
from typing import Dict, Any


class BoardStateModel(BaseModel):
    current_state: Dict[str, Any]
    focus_cards: Dict[str, Any]


class Card(BaseModel):
    name: str
    id: str
    image: str
    metadata: Dict[str, Any]


class RecognizedCards(BaseModel):
    cards: Dict[str, Card]
