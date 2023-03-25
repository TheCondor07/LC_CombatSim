from enum import Enum


class EffectTrigger(Enum):
    ON_HIT = 0
    HEADS_HIT = 1
    ClASH_WIN = 2
    ON_USE = 3
    COMBAT_START = 4
    BEFORE_HIT = 5
    BEFORE_ATTACK = 6
    TAILS_HIT = 7


class EffectDetails(Enum):
    INFLICT_STATUS = 0
    GAIN_STATUS = 1
    INFLICT_STATUS_NEXT_TURN = 2
    GAIN_STATUS_NEXT_TURN = 3
    APPLY_STATUS_COUNT = 4
    GAIN_STATUS_COUNT = 5
    APPLY_STATUS_COUNT_NEXT_TURN = 6
    GAIN_STATUS_COUNT_NEXT_TURN = 7
    RAISE_ATTACK_DAMAGE_MULT = 8
    COIN_DMG_MULT = 9
    COIN_POWER = 10
    HEAL_FOR_DAMAGE = 11
    RAISE_NEXT_COIN = 12
    BOOST_STATUS_OF_FUTURE_COIN = 13
    GIVE_STATUS_TO_LOWEST_ALLY = 14
    SKILL_POWER = 15
    GIVE_STATUS_TO_SLOWEST_ALLY = 16
    BURST_TREMOR = 17
    RAISE_STAGGER_BY_DAMAGE = 18
    APPLY_STATUS_TO_RANDOM_ENEMIES = 19
    REPEAT_COIN = 20
    SPEND_AMMO = 21
    LOSE_HP = 22
    DEAL_PERCENT_BONUS_DAMAGE = 23


class EffectCondition(Enum):
    NO_CONDITION = 0
    TARGET_HAS_STATUS_OF_AMOUNT = 1
    SPEED_IS_HIGHER = 2
    TARGET_ABOVE_HP = 3
    TOOK_NO_DAMAGE_LAST_TURN = 4
    TARGET_TAKEN_DAMAGE = 5
    SPEED_AT_LEAST_X = 6
    SELF_HAS_STATUS_OF_AMOUNT = 7
    TOOK_NO_DAMAGE_THIS_TURN = 8
    TARGET_BELOW_HP = 9
    ON_CRIT = 10
    SELF_BELOW_HP = 11
    TARGET_HAS_LESS_STATUS_OF_AMOUNT = 12
    SPEND_CHARGE = 13

class CoinEffect(Enum):
    HEAL = 0
    RAISE_STAGGER = 1
    DEAL_PERCENT_DAMAGE = 2
