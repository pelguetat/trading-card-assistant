from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class PlayerType(Enum):
    """
    Enum representing the type of player in the game. 
    Can be either a User or an Opponent.
    """
    USER = "User"
    OPPONENT = "Opponent"   

class CardType(Enum):
    """
    Enum representing the type of card in the game. 
    Can be either a Pokemon, Trainer, or Energy card.
    """
    POKEMON = "Pokemon"
    TRAINER = "Trainer"
    ENERGY = "Energy"    

class Card(BaseModel):
    """
    Base model for a card. Contains the type of the card, 
    its in-game ID, and its name.
    """
    type: Optional[CardType] = Field(None, description="The type of the card")
    in_game_id: Optional[int] = Field(None, description="The in-game ID of the card")
    name: Optional[str] = Field(None, description="The name of the card")
    
class Abilities(BaseModel):
    """
    Model for abilities that a Pokemon card may have. 
    Contains the name, text description, and type of the ability.
    """
    name: Optional[str] = Field(None, description="The name of the ability")
    text: Optional[str] = Field(None, description="The text description of the ability")
    type: Optional[str] = Field(None, description="The type of the ability")

class Attacks(BaseModel):
    """
    Model for attacks that a Pokemon card may have. 
    Contains the name, cost, converted energy cost, damage, and text description of the attack.
    """
    name: Optional[str] = Field(None, description="The name of the attack")
    cost: Optional[List[str]] = Field(None, description="The cost of the attack")
    convertedEnergyCost: Optional[int] = Field(None, description="The converted energy cost of the attack")
    damage: Optional[str] = Field(None, description="The damage of the attack")
    text: Optional[str] = Field(None, description="The text description of the attack")

class Weaknesses(BaseModel):
    """
    Model for weaknesses that a Pokemon card may have. 
    Contains the type and value of the weakness.
    """
    type: Optional[str] = Field(None, description="The type of the weakness")
    value: Optional[str] = Field(None, description="The value of the weakness")

class PokemonCard(BaseModel):
    """
    Model for a Pokemon card. Contains various attributes of the card 
    such as ID, name, supertype, subtypes, HP, types, rules, abilities, 
    attacks, weaknesses, retreat cost, converted retreat cost, status conditions, 
    attached energy, attached tools, and damage counters.
    """
    id: Optional[str] = Field(None, description="The ID of the Pokemon card")
    name: Optional[str] = Field(None, description="The name of the Pokemon card")
    supertype: Optional[str] = Field(None, description="The supertype of the Pokemon card")
    subtypes: Optional[List[str]] = Field(None, description="The subtypes of the Pokemon card")
    hp: Optional[str] = Field(None, description="The HP of the Pokemon card")
    types: Optional[List[str]] = Field(None, description="The types of the Pokemon card")
    rules: Optional[List[str]] = Field(None, description="The rules of the Pokemon card")
    abilities: Optional[List[Abilities]] = Field(None, description="The abilities of the Pokemon card")
    attacks: Optional[List[Attacks]] = Field(None, description="The attacks of the Pokemon card")
    weaknesses: Optional[List[Weaknesses]] = Field(None, description="The weaknesses of the Pokemon card")
    retreatCost: Optional[List[str]] = Field(None, description="The retreat cost of the Pokemon card")
    convertedRetreatCost: Optional[int] = Field(None, description="The converted retreat cost of the Pokemon card")
    status_conditions: Optional[List[str]] = Field(None, description="The status conditions of the Pokemon card")
    attached_energy: Optional[List[str]] = Field(None, description="The attached energy of the Pokemon card")
    attached_tools: Optional[List[str]] = Field(None, description="The attached tools of the Pokemon card")
    damage_counters: Optional[int] = Field(None, description="The damage counters of the Pokemon card")


class Player(BaseModel):
    """
    Model for a player in the game. Contains the player's name, hand, 
    prize cards, active Pokemon, bench, discard pile, lost zone, stadium card, 
    and turn actions.
    """
    name: Optional[PlayerType] = Field(None, description="The name of the player")
    hand: Optional[List[str]] = Field(None, description="The hand of the player")
    prize_cards: Optional[List[str]] = Field(None, description="The prize cards of the player")
    active_pokemon: Optional[PokemonCard] = Field(None, description="The active Pokemon of the player")
    bench: Optional[List[PokemonCard]] = Field(None, description="The bench of the player")
    discard_pile: Optional[List[str]] = Field(None, description="The discard pile of the player")
    lost_zone: Optional[List[str]] = Field(None, description="The lost zone of the player")
    stadium_card: Optional[str] = Field(None, description="The stadium card of the player")
    turn_actions: Optional[List[str]] = Field(None, description="The turn actions of the player")

class BoardState(BaseModel):
    """
    Model for the state of the game board. Contains the board, 
    turn number, and the player whose turn it is currently.
    """
    board: Optional[List[Player]] = Field(None, description="The board state")
    turn_number: Optional[int] = Field(None, description="The turn number")
    current_turn: Optional[PlayerType] = Field(None, description="The player whose turn it is currently")
    
class TrainerCard(BaseModel):
    """
    Model for a Trainer card. Contains the name, text description, 
    and trainer rule of the card.
    """
    name: Optional[str] = Field(None, description="The name of the Trainer card")
    text: Optional[str] = Field(None, description="The text description of the Trainer card")
    trainer_rule: Optional[str] = Field(None, description="The trainer rule of the Trainer card")

class EnergyCard(BaseModel):
    """
    Model for an Energy card. Contains the type of energy the card provides.
    """
    energy_type: Optional[str] = Field(None, description="The type of energy the Energy card provides")
