import math
from enum import Enum

import configs


class EndOfTurn(Enum):
    NOTHING = 0
    LOWER_COUNT = 1
    REMOVE = 2
    HALVE = 3
    TALISMAN = 4


class StatusDef:
    def __init__(self, name: str, end_of_turn=EndOfTurn.NOTHING, count_only=False, max=0, negative=False):
        self.name = name
        self.end_of_turn = end_of_turn
        self.count_only = count_only
        self.max = max
        self.negative = negative

    def __str__(self):
        return self.name

    name: str
    end_of_turn: EndOfTurn
    count_only: bool
    max: int
    negative: bool


class Status:
    def __init__(self, status: StatusDef, amount, combatant, count=1):
        self.type = status
        self.combatant = combatant

        if status.count_only:
            self.amount = 0
            if count > 1:
                self.count = count
            else:
                self.count = amount
        else:
            self.amount = amount
            self.count = count

    type: StatusDef
    amount: int
    count: int = 1
    combatant = None

    def get_count(self):
        return self.count

    def get_amount(self):
        if self.type.count_only:
            return self.get_count()
        else:
            return self.amount

    def change_amount(self, amount):
        if self.type.count_only:
            return self.change_count(amount)
        else:
            self.amount += amount

            if self.amount == 0:
                return True

        return False

    def change_count(self, count):
        self.count += count

        if self.type.max > 0:
            self.count = min(self.count, self.type.max)

        if self.count <= 0:
            return True
        else:
            return False

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
        elif self.type.end_of_turn == EndOfTurn.TALISMAN:
            if self.count >= 6:
                self.combatant.damage(self.count)
                if configs.COMBAT_VERBOSE:
                    print(f"{self.combatant.sinner.name}'s Talismans have burst, {self.count} damage.")
                return True
            else:
                return False
        else:
            return False

    def is_negative(self):
        return self.type.negative


class StatusType:
    ATTACK_POWER_UP = StatusDef("Attack Power Up", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    ATTACK_POWER_DOWN = StatusDef("Attack Power Down", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    BIND = StatusDef("Bind", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    SINKING = StatusDef("Sinking", negative=True)
    RUPTURE = StatusDef("Rupture", negative=True)
    POISE = StatusDef("Poise", end_of_turn=EndOfTurn.LOWER_COUNT)
    SLASH_DAMAGE_UP = StatusDef("Slash Damage Up", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    PIERCE_DAMAGE_UP = StatusDef("Pierce Damage Up", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    BLUNT_DAMAGE_UP = StatusDef("Blunt Damage Up", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    BLEED = StatusDef("Bleed", negative=True)
    BURN = StatusDef("Burn", end_of_turn=EndOfTurn.LOWER_COUNT, negative=True)
    HASTE = StatusDef("Haste", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    TREMOR = StatusDef("Tremor", end_of_turn=EndOfTurn.LOWER_COUNT, negative=True)
    DEFENSE_LEVEL_UP = StatusDef("Defense Level Up", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    DEFENSE_LEVEL_DOWN = StatusDef("Defense Level Down", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    OFFENSE_LEVEL_UP = StatusDef("Offense Level Up", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    OFFENSE_LEVEL_DOWN = StatusDef("Offense Level Down", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    PROTECTION = StatusDef("Protection", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    DEFENSE_POWER_UP = StatusDef("Defense Power Up", end_of_turn=EndOfTurn.REMOVE, count_only=True)  # TODO: Implement Defense Power Up
    DEFENSE_POWER_DOWN = StatusDef("Defense Power Down", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)  # TODO: Implement Defense Power Down
    SLASH_FRAGILITY = StatusDef("Slash Fragility", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10, negative=True)
    PIERCE_FRAGILITY = StatusDef("Pierce Fragility", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10, negative=True)
    BLUNT_FRAGILITY = StatusDef("Blunt Fragility", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10, negative=True)
    DAMAGE_UP = StatusDef("Damage Up", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    DAMAGE_DOWN = StatusDef("Damage Down", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10, negative=True)
    PARALYZE = StatusDef("Paralyze", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    FRAGILE = StatusDef("Fragile", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10, negative=True)
    FANATIC = StatusDef("Fanatic", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    NAILS = StatusDef("Nails", end_of_turn=EndOfTurn.HALVE, count_only=True, negative=True)
    PLUS_COIN_DROP = StatusDef("Plus Coin Drop", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    CHARGE = StatusDef("Charge", end_of_turn=EndOfTurn.LOWER_COUNT, count_only=True, max=20)
    SLASH_PROTECTION = StatusDef("Slash Protection", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    PIERCE_PROTECTION = StatusDef("Pierce Protection", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    BLUNT_PROTECTION = StatusDef("Blunt Protection", end_of_turn=EndOfTurn.REMOVE, count_only=True, max=10)
    GAZE = StatusDef("Gaze", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)  # TODO: Implement SP Gain
    WEAKNESS_ANALYZED = StatusDef("Weakness Analyzed", end_of_turn=EndOfTurn.REMOVE, count_only=True, negative=True)
    TALISMAN = StatusDef("Talisman", end_of_turn=EndOfTurn.TALISMAN, count_only=True, negative=True)
    SHIELD = StatusDef("Shield", end_of_turn=EndOfTurn.REMOVE, count_only=True)
    CHARGE_BARRIER = StatusDef("Charge Barrier", end_of_turn=EndOfTurn.REMOVE, count_only=True)
