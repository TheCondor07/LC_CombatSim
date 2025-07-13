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
    ON_DISCARD = 11
    ALLY_DEATH = 12
    ENEMY_DEATH = 13
    ON_KILL = 15
    ON_BURST = 16
    STAGGER_RECOVER = 17
    ATTACKED = 18


class EffectDetails(Enum):
    GIVE_STATUS = 1
    GIVE_STATUS_NEXT_TURN = 2
    GIVE_STATUS_COUNT = 3
    GIVE_STATUS_COUNT_NEXT_TURN = 4
    REMOVE_STATUS = 5
    SKILL_POWER = 6
    COIN_POWER = 7
    RAISE_NEXT_COIN = 8
    RAISE_ATTACK_DAMAGE_MULT = 9
    COIN_DMG_MULT = 10  # Phase 3 damage increase for one coin
    HEAL_FOR_DAMAGE = 11
    BOOST_STATUS_COUNT_OF_FUTURE_COIN = 12  # Amount = How much to boost, extra = coin to boost
    BURST_TREMOR = 13
    RAISE_STAGGER_BY_DAMAGE = 14
    LOWER_SELF_STAGGER_BY_DAMAGE = 15
    REPEAT_COIN = 16
    SPEND_AMMO = 17
    GAIN_SP = 18
    GAIN_HP = 19
    DEAL_PERCENT_BONUS_DAMAGE = 20  # Meant for specific coins that deal extra damage after all damage is dealt
    DOUBLE_CRIT_CHANCE = 21
    TARGET_RANDOM = 22
    ADDED_DAMAGE = 23
    GAIN_PERCENT_HP = 24
    NEG_SP_TO_CRIT = 25
    CLASH_POWER = 26
    DISCARD_LOWEST = 27
    HP_FOR_STATUS = 28  # Target = who to give hp (negative to damage), Target2 = Who to count status on
    GIVE_STATUS_COUNT_FOR_COUNT = 29  # Target = who to give count, Target2 = Who to count status on, Status2 = status to check
    BONUS_CRIT_DAMAGE = 30
    MULT_OVERALL_DAMAGE_DONE = 31
    MULT_DAMAGE_TAKEN = 32
    GAIN_SP_NEXT_TURN = 33
    GIVE_STATUS_PER_BURST = 34
    BOOSTED_TREMOR_BURST = 35
    BOOST_STATUS_AMOUNT_OF_FUTURE_COIN = 36
    GIVE_STATUS_PER_HP = 37


class EffectCondition(Enum):
    STATUS_OF_AMOUNT = 1
    STATUS_LESS_THAN_AMOUNT = 2
    STATUS_OF_COUNT = 3
    STATUS_LESS_THAN_COUNT = 4
    SPEED_IS_HIGHER = 5
    SPEED_AT_LEAST_X = 6
    ABOVE_HP_PERCENT = 7
    BELOW_HP_PERCENT = 8
    LESS_THAN_SP = 9
    MORE_THAN_SP = 10
    TOOK_NO_DAMAGE_THIS_TURN = 11
    TOOK_NO_DAMAGE_LAST_TURN = 12
    TAKEN_DAMAGE = 13
    ON_CRIT = 14
    ON_COIN = 15
    GOT_HEADS = 16
    SPEND_STATUS = 17
    HAS_SPENT = 18
    HIGHER_MAX_HP = 19
    HAS_NEGATIVE_STATUS = 20
    CLASH_WON = 21
    PASSIVE_ACTIVE = 22
    NEXT_SKILL_MATCHES_DAMAGE_TYPE = 23
    DID_NO_DAMAGE_LAST_TURN = 24


class CoinEffect(Enum):
    HEAL = 0
    RAISE_STAGGER = 1
    DEAL_PERCENT_DAMAGE = 2
    LOWER_OWN_STAGGER = 3
    PHASE_4_DAMAGE = 4


class EffectTarget(Enum):
    SELF = 1
    TARGET = 2
    LOWEST_ALLY = 3
    PLACED_AFTER = 4
    PLACED_BEFORE = 5
    SLOWEST_ALLY = 6
    RANDOM = 7
