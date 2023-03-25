import math
from enum import Enum


class EndOfTurn(Enum):
    NOTHING = 0
    LOWER_COUNT = 1
    REMOVE = 2
    HALVE = 3


class StatusDef:
    def __init__(self, name: str, end_of_turn=EndOfTurn.NOTHING):
        self.name = name
        self.end_of_turn = end_of_turn

    def __str__(self):
        return self.name

    name: str
    end_of_turn: EndOfTurn


class Status:
    def __init__(self, status: StatusDef, amount, count=1):
        self.type = status
        self.amount = amount
        self.count = count

    type: StatusDef
    amount: int
    count: int = 1

    # Returns true if the status should be removed
    def end_of_turn(self):
        if self.type.end_of_turn == EndOfTurn.LOWER_COUNT:
            self.count -= 1

            if self.count == 0:
                return True
            else:
                return False
        elif self.type.end_of_turn == EndOfTurn.REMOVE:
            return True
        elif self.type.end_of_turn == EndOfTurn.HALVE:
            self.count = self.count // 2
            if self.count == 0:
                return True
            else:
                return False
        else:
            return False


class StatusType:
    ATTACK_POWER_UP = StatusDef("Attack Power Up", end_of_turn=EndOfTurn.REMOVE)
    ATTACK_POWER_DOWN = StatusDef("Attack Power Down", end_of_turn=EndOfTurn.REMOVE)
    BIND = StatusDef("Bind", end_of_turn=EndOfTurn.REMOVE)
    SINKING = StatusDef("Sinking")
    RUPTURE = StatusDef("Rupture")
    POISE = StatusDef("Poise", end_of_turn=EndOfTurn.LOWER_COUNT)
    SLASH_DAMAGE_UP = StatusDef("Slash Damage Up", end_of_turn=EndOfTurn.REMOVE)
    PIERCE_DAMAGE_UP = StatusDef("Pierce Damage Up", end_of_turn=EndOfTurn.REMOVE)
    BLUNT_DAMAGE_UP = StatusDef("Blunt Damage Up", end_of_turn=EndOfTurn.REMOVE)
    BLEED = StatusDef("Bleed")
    BURN = StatusDef("Burn", end_of_turn=EndOfTurn.LOWER_COUNT)
    HASTE = StatusDef("Haste", end_of_turn=EndOfTurn.REMOVE)
    TREMOR = StatusDef("Tremor", end_of_turn=EndOfTurn.LOWER_COUNT)
    DEFENSE_LEVEL_UP = StatusDef("Defense Level Up", end_of_turn=EndOfTurn.REMOVE)
    DEFENSE_LEVEL_DOWN = StatusDef("Defense Level Down", end_of_turn=EndOfTurn.REMOVE)
    OFFENSE_LEVEL_UP = StatusDef("Offense Level Up", end_of_turn=EndOfTurn.REMOVE)
    OFFENSE_LEVEL_DOWN = StatusDef("Offense Level Down", end_of_turn=EndOfTurn.REMOVE)
    PROTECTION = StatusDef("Protection", end_of_turn=EndOfTurn.REMOVE)
    DEFENSE_POWER_UP = StatusDef("Defense Power Up", end_of_turn=EndOfTurn.REMOVE)  # TODO: Implement Defense Power Up
    DEFENSE_POWER_DOWN = StatusDef("Defense Power Down", end_of_turn=EndOfTurn.REMOVE)  # TODO: Implement Defense Power Down
    SLASH_FRAGILITY = StatusDef("Slash Fragility", end_of_turn=EndOfTurn.REMOVE)
    PIERCE_FRAGILITY = StatusDef("Pierce Fragility", end_of_turn=EndOfTurn.REMOVE)
    BLUNT_FRAGILITY = StatusDef("Blunt Fragility", end_of_turn=EndOfTurn.REMOVE)
    DAMAGE_UP = StatusDef("Damage Up", end_of_turn=EndOfTurn.REMOVE)
    DAMAGE_DOWN = StatusDef("Damage Down", end_of_turn=EndOfTurn.REMOVE)
    PARALYZE = StatusDef("Paralyze", end_of_turn=EndOfTurn.REMOVE)
    FRAGILE = StatusDef("Fragile", end_of_turn=EndOfTurn.REMOVE)
    FANATIC = StatusDef("Fanatic", end_of_turn=EndOfTurn.REMOVE)
    NAILS = StatusDef("Nails", end_of_turn=EndOfTurn.HALVE)
    PLUS_COIN_DROP = StatusDef("Plus Coin Drop", end_of_turn=EndOfTurn.REMOVE)
    CHARGE = StatusDef("Charge", end_of_turn=EndOfTurn.LOWER_COUNT)
