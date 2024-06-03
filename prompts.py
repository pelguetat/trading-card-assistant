PROMPT = """
You are a Pokemon Trading Card Game tutor. Your purpose is to assist the player  in learning the game.
The rules of the game are as follows:
{{
  "Deck_Building": {
    "Size": "60 cards",
    "Card_Limits": {
      "Basic_Energy": "Unlimited",
      "Other_Cards": "Maximum 4 copies of the same card name"
    },
    "Minimum_Basic_Pokémon": "At least one"
  },
  "Win_Conditions": [
    "Take all of your Prize cards",
    "Knock Out all of your opponent’s Pokémon in play",
    "Opponent has no cards in their deck at the beginning of their turn"
  ],
  "Setup": [
    "Shake hands with your opponent",
    "Flip a coin to decide who goes first",
    "Shuffle your deck and draw 7 cards",
    "Check for Basic Pokémon in your hand",
    "Place one Basic Pokémon as Active Pokémon",
    "Place up to 5 Basic Pokémon on the Bench",
    "Set aside top 6 cards of your deck as Prize cards",
    "Both players reveal their Active and Benched Pokémon"
  ],
  "Turn_Parts": [
    "Draw a card",
    {
      "Actions": [
        "Put Basic Pokémon cards from your hand onto your Bench",
        "Evolve your Pokémon",
        "Attach an Energy card to one of your Pokémon",
        "Play Trainer cards",
        "Retreat your Active Pokémon",
        "Use Abilities"
      ],
      "Order": "Any order"
    },
    "Attack and end your turn"
  ],
  "Appendices": {
    "ACE_SPEC_Cards": {
      "Introduction": "Black & White Series",
      "Limit": "Only one ACE SPEC card per deck"
    },
    "Ancient_and_Future_Cards": {
      "Introduction": "Scarlet & Violet—Paradox Rift expansion",
      "Ancient": "Primitive, hard-hitting attacks",
      "Future": "Technical, precise attacks"
    },
    "Pokémon_ex": {
      "Characteristics": "More HP and stronger attacks",
      "Risk": "Opponent takes 2 Prize cards when Knocked Out",
      "Naming": "Different from regular Pokémon (e.g., Miraidon vs. Miraidon ex)"
    },
    "Lost_Zone": {
      "Description": "Unique zone, out of play",
      "Recovery": "Cannot be recovered or played again"
    },
    "Tera_Pokémon_ex": {
      "Appearance": "Crystalline",
      "Effect": "Prevents all attack damage while on Bench"
    },
    "Pokémon_VSTAR": {
      "Characteristics": "Special Ability or attack called VSTAR Power",
      "Limit": "Only one VSTAR Power per game",
      "Knock_Out_Risk": "Opponent takes 2 Prize cards when Knocked Out"
    }
  }
}}

"""

BOARD_STATE = {
    "board": [
        {
            "name": "Opponent",
            "deck": ["number of cards left in the deck"],
            "hand": ["number of cards in the hand"],
            "prize_cards": ["number of prize cards left"],
            "active_pokemon": {
                "name": "Pikachu",
                "hp": 60,
                "status_conditions": ["paralyzed"],
                "attached_energy": ["Electric Energy", "Electric Energy"],
                "attached_tools": ["Tool1"],
                "damage_counters": 30,
            },
            "bench": [
                {
                    "name": "Charmander",
                    "hp": 50,
                    "status_conditions": [],
                    "attached_energy": ["Fire Energy"],
                    "attached_tools": [],
                    "damage_counters": 0,
                },
                {
                    "name": "Bulbasaur",
                    "hp": 60,
                    "status_conditions": [],
                    "attached_energy": [],
                    "attached_tools": [],
                    "damage_counters": 10,
                },
            ],
            "discard_pile": ["card7", "card8", "..."],
            "lost_zone": ["card9", "card10", "..."],
            "stadium_card": "Stadium1",
            "turn_actions": ["draw", "attach_energy", "attack"],
        },
        {
            "name": "Player",
            "deck": ["number of cards left in the deck"],
            "hand": ["card13", "card14", "..."],
            "prize_cards": ["number of prize cards left"],
            "active_pokemon": {
                "name": "Squirtle",
                "hp": 50,
                "status_conditions": ["burned"],
                "attached_energy": ["Water Energy"],
                "attached_tools": [],
                "damage_counters": 20,
            },
            "bench": [
                {
                    "name": "Eevee",
                    "hp": 50,
                    "status_conditions": [],
                    "attached_energy": ["Colorless Energy"],
                    "attached_tools": [],
                    "damage_counters": 0,
                }
            ],
            "discard_pile": ["card17", "card18", "..."],
            "lost_zone": ["card19", "card20", "..."],
            "stadium_card": "Stadium2",
            "turn_actions": ["draw", "play_trainer", "retreat"],
        },
    ],
    "current_turn": "Player",
    "turn_phase": "attack",
    "coin_flip_result": "heads",
}

POKEMON_CARD = (
    {
        "name": "Squirtle",
        "hp": 50,
        "status_conditions": ["burned"],
        "attached_energy": ["Water Energy"],
        "attached_tools": [],
        "damage_counters": 20,
    },
)
