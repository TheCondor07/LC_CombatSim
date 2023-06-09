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
    ClASH_LOSE = 8
    BEFORE_DAMAGE = 9
    ON_CLASH = 10


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
    DOUBLE_CRIT_CHANCE = 24
    LOWER_SELF_STAGGER_BY_DAMAGE = 25
    TARGET_RANDOM = 26
    REMOVE_STATUS = 27
    ADDED_DAMAGE = 28
    LOSE_PERCENT_HP = 29
    NEG_SP_TO_CRIT = 30
    HEAL_SP = 31
    TARGET_LOSE_SP = 32
    REDUCE_CLASH_POWER = 33


class EffectCondition(Enum):
    TARGET_HAS_STATUS_OF_AMOUNT = 1
    SPEED_IS_HIGHER = 2
    TARGET_ABOVE_HP = 3
    TOOK_NO_DAMAGE_LAST_TURN = 4
    TARGET_TAKEN_DAMAGE= 5
    SPEED_AT_LEAST_X = 7
    SELF_HAS_STATUS_OF_AMOUNT = 8
    TOOK_NO_DAMAGE_THIS_TURN = 9
    TARGET_BELOW_HP = 10
    ON_CRIT = 11
    SELF_BELOW_HP = 12
    TARGET_HAS_LESS_STATUS_OF_AMOUNT = 13
    SPEND_CHARGE = 14
    TARGET_HAS_STATUS_OF_COUNT = 15
    SELF_HAS_STATUS_BELOW_COUNT = 16
    ON_COIN = 17
    GOT_HEADS = 18
    TARGET_HAS_LESS_THAN_SP = 19
    SELF_HAS_LESS_THAN_SP = 20
    SELF_HAS_MORE_THAN_SP = 21



class CoinEffect(Enum):
    HEAL = 0
    RAISE_STAGGER = 1
    DEAL_PERCENT_DAMAGE = 2
    LOWER_OWN_STAGGER = 3
    PHASE_4_DAMAGE = 4
