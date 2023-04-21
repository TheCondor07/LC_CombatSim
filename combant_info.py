import copy
import math
import random
import typing

import configs
import tools
from effects import EffectTrigger, EffectDetails, EffectCondition, CoinEffect
from sin_types import Sin
from statuses import StatusType, Status, StatusDef


class Sinner(typing.NamedTuple):
    name: str
    hp: int
    spd_min: int
    spd_max: int
    def_base: int
    off_base: int
    res: list
    stagger: list
    skills: list
    passive: Passive = None


class Skill(typing.NamedTuple):
    name: str
    sin: Sin
    type: int  # 0=Slash, 1=Pierce, 2=Blunt
    base: int
    coin_bonus: int
    coin_num: int
    general_effects: list
    coin_effects: list


class Passive(typing.NamedTuple):
    name: str
    sin: Sin
    amount_required: int
    use_pool: bool
    effects: list


class CombatStats:
    def __init__(self, sinner):
        self.sinner = sinner
        self.hp = sinner.hp
        self.statuses = list()
        self.status_next_turn = list()
        self.combat_deck = list()
        self.skill_slots = list()
        self.status_count_next_turn = list()
        self.speed = 0
        self.sp = configs.STARTING_SANITY

        self.gain_skill_slot()

    def __str__(self):
        return self.sinner.name

    sinner: Sinner
    hp = 0
    sp = 0
    statuses: list
    status_next_turn: list
    status_count_next_turn: list
    combat_deck: list
    damaged_this_turn = False
    damaged_last_turn = False
    speed: int
    skill_slots: list
    team = None
    next_stagger_threshold = 0
    stagger_level = 0
    staggered_last_turn = False
    stagger_threshold_offset = 0
    ammo = 13

    def gain_skill_slot(self):
        self.combat_deck.append(list())
        self.skill_slots.append(list())

    def choose_skill(self, skill_slot, opponent, targeted_skill_slot):
        if self.stagger_level == 0:
            if len(self.combat_deck[skill_slot]) < 2:
                new_deck = [0, 0, 0, 1, 1, 2]
                random.shuffle(new_deck)
                self.combat_deck[skill_slot] += new_deck

            skill_ranking = [self.rank_skill(self.combat_deck[skill_slot][0]), self.rank_skill(self.combat_deck[skill_slot][1])]
            if skill_ranking[0] >= skill_ranking[1]:
                chosen_skill = self.combat_deck[skill_slot][0]
            else:
                chosen_skill = self.combat_deck[skill_slot][1]

            self.skill_slots[skill_slot] = CombatSkill(self.sinner.skills[chosen_skill], self, opponent, targeted_skill_slot)
            self.combat_deck[skill_slot].remove(chosen_skill)
        else:
            return -1

    def rank_skill(self, skill):
        if self.sinner.skills[skill].name == "Rip Space" and not self.get_status_count(StatusType.CHARGE) >= 10:
            return -1
        else:
            return skill

    def get_off(self):
        return math.floor(self.sinner.off_base * (1-0.1*self.get_status_amount(StatusType.OFFENSE_LEVEL_DOWN) +
                          0.1*self.get_status_amount(StatusType.OFFENSE_LEVEL_UP)))

    def get_def(self):
        return math.floor(self.sinner.def_base * (1 - 0.1 * self.get_status_amount(StatusType.DEFENSE_LEVEL_DOWN) +
                                           0.1 * self.get_status_amount(StatusType.DEFENSE_LEVEL_UP)))

    def get_resistance(self, skill: Skill):
        if configs.USE_STAGGER and self.stagger_level > 0:
            return 50 + self.stagger_level * 50
        elif configs.USE_RESISTANCE:
            return self.sinner.res[skill.type]
        else:
            return 0

    def get_stagger_threshold(self):
        if len(self.sinner.stagger) > self.next_stagger_threshold:
            return math.floor(self.sinner.hp * (self.sinner.stagger[self.next_stagger_threshold]) / 100) + self.stagger_threshold_offset
        else:
            return 0

    def remove_status(self, status_to_remove: StatusDef):
        for status in self.statuses:
            if status.type == status_to_remove:
                self.statuses.remove(status)

                return

    def lower_status_count(self, status_to_lower: StatusDef, amount=1):
        status_found = False
        new_count = 0

        for status in self.statuses:
            if status.type == status_to_lower:
                if status.change_count(-1 * amount):
                    self.statuses.remove(status)
                new_count = status.count
                status_found = True

        if status_found:
            if configs.COMBAT_VERBOSE:
                print(f"{self.sinner.name}'s {status_to_lower}'s count lowered by {amount} (now {new_count})")

    def lower_status_amount(self, status_to_lower: StatusDef):
        status_found = False
        new_amount = 0

        for status in self.statuses:
            if status.type == status_to_lower:
                if status.change_amount(-1):
                    self.statuses.remove(status)

                status_found = True
                new_amount = status.get_amount()

        if status_found:
            if configs.COMBAT_VERBOSE:
                print(f"{self.sinner.name}'s {status_to_lower}'s amount lowered by 1 (now {new_amount})")

    def raise_status_count(self, status_to_raise: StatusDef, count: int):
        status_not_found = True
        new_count = count

        for status in self.statuses:
            if status.type == status_to_raise:
                if not status_not_found:
                    print(f"Warning: Duplicate status {status_to_raise} found on {self.sinner.name}")

                status.change_count(count)
                new_count = status.get_count()

                status_not_found = False

        if status_not_found:
            self.statuses.append(Status(status_to_raise, 1, count=count))

        if configs.COMBAT_VERBOSE:
            print(f"{self.sinner.name}'s {status_to_raise} gains {count} count (now {new_count})")

    def apply_status(self, status: Status):
        status_not_found = True
        new_status_amount = 0
        new_status_count = 0
        for checked_status in self.statuses:
            if status.type == checked_status.type:
                if not status_not_found:
                    print(f"Warning: Duplicate status {status.type} found on {self.sinner.name}")

                checked_status.change_amount(status.get_amount())
                new_status_amount = checked_status.get_amount()
                new_status_count = checked_status.get_count()
                status_not_found = False
                break

        if status_not_found:
            self.statuses.append(copy.copy(status))
            new_status_amount = status.amount
            new_status_count = status.count

        if configs.COMBAT_VERBOSE:
            print(f"{self.sinner.name} gains {status.get_amount()} {status.type}, now ({new_status_count}, {new_status_amount})")

    def apply_status_next_turn(self, status: Status):
        self.status_next_turn.append(status)

    def raise_status_count_next_turn(self, status_to_raise: StatusDef, count: int):
        self.status_count_next_turn.append([status_to_raise, count])

    def end_of_turn(self):
        burn = self.get_status_amount(StatusType.BURN)

        if burn > 0:
            self.hp -= burn
            if configs.COMBAT_VERBOSE:
                print(f"{self.sinner.name} has taken {burn} burn damage.")

        statuses_to_remove = list()
        for status in self.statuses:
            if status.end_of_turn():
                statuses_to_remove.append(status)

        for status in statuses_to_remove:
            self.statuses.remove(status)

        for status in self.status_next_turn:
            self.apply_status(status)

        for status in self.status_count_next_turn:
            self.raise_status_count(status[0], status[1])

        self.status_next_turn = []
        self.status_count_next_turn = []

        self.damaged_last_turn = self.damaged_this_turn
        self.damaged_this_turn = False

        nails = self.get_status_count(StatusType.NAILS)
        if nails > 0:
            self.apply_status(Status(StatusType.BLEED, 1))
            self.raise_status_count(StatusType.BLEED, nails)

        if self.stagger_level > 0:
            if self.staggered_last_turn:
                self.stagger_level = 0
                self.staggered_last_turn = False
            else:
                self.staggered_last_turn = True

    def get_status_amount(self, status_type: StatusDef):
        for status in self.statuses:
            if status.type == status_type:
                return status.get_amount()

        return 0

    def get_status_count(self, status_type: StatusDef):
        for status in self.statuses:
            if status.type == status_type:
                return status.get_count()

        return 0

    def speed_roll(self):
        self.speed = random.randrange(self.sinner.spd_min, self.sinner.spd_max+1) + self.get_status_amount(StatusType.HASTE) - self.get_status_amount(StatusType.BIND)

    def bleed(self):
        bleed = self.get_status_amount(StatusType.BLEED)

        if bleed > 0:
            self.hp -= bleed
            self.lower_status_count(StatusType.BLEED)
            if configs.COMBAT_VERBOSE:
                print(f"{self.sinner.name} has taken {bleed} bleed damage.")

    def coin_flip(self):
        if random.randrange(100) < 50 + self.sp:
            return True
        else:
            return False

    def damage(self, damage: int):
        self.hp -= damage

        if damage > 0:
            self.damaged_this_turn = True

        if configs.COMBAT_VERBOSE and self.hp <= 0:
            print(f"{self} has died.")
        else:
            if configs.USE_STAGGER:
                while True:
                    if len(self.sinner.stagger) > self.next_stagger_threshold:
                        if self.get_stagger_threshold() >= self.hp:
                            if not self.staggered_last_turn:
                                self.stagger_level += 1
                                if configs.COMBAT_VERBOSE:
                                    print(f"{self.sinner.name} is staggered!")
                            self.next_stagger_threshold += 1
                            self.stagger_threshold_offset = 0
                        else:
                            break
                    else:
                        break

    def heal(self, heal_amount):
        old_hp = self.hp
        self.hp = min(old_hp + heal_amount, self.sinner.hp)

        if self.hp != old_hp:
            if configs.COMBAT_VERBOSE:
                print(f"{self.sinner.name} heals for {self.hp - old_hp}")

    def gain_lose_sp(self, sp):
        old_sp = self.sp
        self.sp = max(min(self.sp + sp, 45), -45)

        if self.sp != old_sp:
            if configs.COMBAT_VERBOSE:
                if sp < 0:
                    print(f"{self.sinner.name} loses {old_sp - self.sp} sp (now {self.sp})")
                else:
                    print(f"{self.sinner.name} gains {self.sp - old_sp} sp (now {self.sp})")

    def add_stagger_offset(self, amount):
        self.stagger_threshold_offset = max(min(self.stagger_threshold_offset + amount, self.hp), 0)

        if self.stagger_threshold_offset:
            if len(self.sinner.stagger) > self.next_stagger_threshold + 1:
                if self.get_stagger_threshold() < math.floor(self.sinner.hp * (self.sinner.stagger[self.next_stagger_threshold+1]) / 100):
                    self.stagger_threshold_offset = 0
                    self.next_stagger_threshold += 1
                    print("Stagger threshold removed from lowering it")

        if configs.FULL_DEBUG:
            print(f"Raising {self.sinner.name}'s stagger by {amount}.")

    def spend_charge(self, amount):
        charge = self.get_status_count(StatusType.CHARGE)
        if charge >= amount:
            self.lower_status_count(StatusType.CHARGE, amount=amount)
            return True
        else:
            return False

    def can_act(self):
        if self.stagger_level == 0 and self.hp >= 0:
            return True
        else:
            return False


class Team:
    def __init__(self):
        self.sinners = list()

    def __str__(self):
        sinner_strs = []
        for sinner in self.sinners:
            sinner_strs.append(str(sinner))

        return ", ".join(sinner_strs)

    sinners: list
    turn_order: list
    opponents = None

    def get_lowest_hp(self):
        alive_sinners = self.get_alive_sinners()
        random.shuffle(alive_sinners)
        lowest = None

        for sinner in alive_sinners:
            if lowest is None:
                lowest = sinner
            elif sinner.hp < lowest.hp:
                lowest = sinner

        return lowest

    def get_slowest(self):
        alive_sinners = self.get_alive_sinners()
        random.shuffle(alive_sinners)
        slowest = None

        for sinner in alive_sinners:
            if slowest is None:
                slowest = sinner
            if sinner.speed < slowest.speed:
                slowest = sinner

        return slowest

    def get_alive_sinners(self):
        alive_sinners = list()

        for sinner in self.sinners:
            if sinner.hp > 0:
                alive_sinners.append(sinner)

        return alive_sinners

    def add_to_team(self, sinners: list):
        for sinner in sinners:
            combatant = CombatStats(sinner)
            self.sinners.append(combatant)
            combatant.team = self

    def get_random(self, number: int, excludes: list = None):
        sinners = self.get_alive_sinners()

        if excludes is not None:
            for exclude in excludes:
                sinners.remove(exclude)

        random.shuffle(sinners)

        return sinners[:(number-len(sinners))]

    def choose_skills(self):
        reverse_opposing_turn_order: list = self.opponents.turn_order.copy()
        reverse_opposing_turn_order.reverse()

        targeting_order = []
        for opponent in reverse_opposing_turn_order:
            for skill_slot in range(len(opponent.skill_slots)):
                targeting_order.append([opponent, skill_slot])

        i = 0
        for combatant in self.turn_order:
            for skill_slot in range(len(combatant.skill_slots)):
                combatant.choose_skill(skill_slot, targeting_order[i][0], targeting_order[i][1])
                i += 1
                if i >= len(targeting_order):
                    i = 0

    def add_skill_slot(self):
        sinners = self.get_alive_sinners()
        random.shuffle(sinners)
        chosen_sinner = None
        staggered_sinner = None

        for sinner in sinners:
            if sinner.stagger_level > 0:
                if staggered_sinner is None:
                    staggered_sinner = sinner
                elif len(staggered_sinner.skill_slots) > len(sinner.skill_slots):
                    staggered_sinner = sinner
            else:
                if chosen_sinner is None:
                    chosen_sinner = sinner
                elif len(chosen_sinner.skills_slots) > len(sinner.skill_slots):
                    chosen_sinner = sinner

        if chosen_sinner is None:
            staggered_sinner.gain_skill_slot()
        else:
            chosen_sinner.gain_skill_slot()


class CombatSkill:
    def __init__(self, skill: Skill, combatant: CombatStats, opponent: CombatStats, targeted_slot: int):
        self.skill = skill
        self.combatant = combatant
        self.opponent = opponent
        self.coins = skill.coin_num
        self.targeted_slot = targeted_slot

        self.base_damage_sources = list()
        self.phase_3_mult_bonus_sources = list()
        self.phase_3_coin_specific = list()
        self.specific_coin_power_bonus = list()
        self.effect_on_coin_damage = list()
        self.repeat_coins = [0] * self.coins
        self.coin_effects = skill.coin_effects.copy()
        self.trigger_effect(EffectTrigger.COMBAT_START)

    coins: int
    coin_effects: list
    skill: Skill
    combatant: CombatStats
    opponent: CombatStats
    targeted_slot = -1

    # Damage and combat stats
    total_base_damage = 0
    base_damage_sources = list()
    phase_3_mult_bonus = 0
    phase_3_mult_bonus_sources = list()
    phase_3_coin_specific = list()
    coin_power_bonus = 0
    skill_power_bonus = 0
    specific_coin_power_bonus = list()
    effect_on_coin_damage = list()
    is_critical = False
    double_crit_chance = False
    spent_ammo = True
    skip_attack = False
    status_boost = 0  # How much bonus amount a status inflicted or applied will get
    has_been_used = False
    can_be_clashed = True
    crit_bonus = 0
    clash_power = 0

    def __str__(self):
        return self.skill.name

    def get_skill_power(self, bonus_sources: list = None):
        skill_power = self.skill.base
        if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
            bonus_sources.append(["Base", self.skill.base])

        # Temp variable to avoid repeated searches of statuses
        bonus_check = self.combatant.get_status_amount(StatusType.ATTACK_POWER_UP)
        if bonus_check > 0:
            skill_power += bonus_check
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Attack Power Up", bonus_check])
        bonus_check = self.combatant.get_status_amount(StatusType.ATTACK_POWER_DOWN)
        if bonus_check > 0:
            skill_power -= bonus_check
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Attack Power Down", bonus_check * -1])
        if self.skill_power_bonus != 0:
            skill_power += bonus_check
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Skill Effects", self.skill_power_bonus])
        bonus_check = self.combatant.get_off() - self.opponent.get_off()
        if bonus_check >= 5:
            bonus_check = bonus_check//5
            skill_power += bonus_check
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Offense", bonus_check])
        fanatic = self.combatant.get_status_amount(StatusType.FANATIC)
        if fanatic > 0 and self.opponent.get_status_count(StatusType.NAILS) > 0:
            skill_power += fanatic
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Fanatic", fanatic])

        return skill_power

    # Does a flip and pops paralyze. Returns a list, first element is power, second element is bool of 'is heads'
    def get_coin_power(self, coin: int, bonus_sources: list = None):
        is_heads = self.combatant.coin_flip()

        if self.combatant.get_status_amount(StatusType.PARALYZE) == 0:
            if is_heads:
                coin_power = self.coin_power_bonus + self.skill.coin_bonus
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    bonus_sources.append(["Heads", self.skill.coin_bonus])
                    if self.coin_power_bonus != 0:
                        bonus_sources.append(["Skill Effect", self.coin_power_bonus])

                    for power_boost in self.specific_coin_power_bonus:
                        if power_boost[0] == coin:
                            coin_power += power_boost[1]
                            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                                bonus_sources.append(["Skill Effect", power_boost[1]])

                bonus_check = self.combatant.get_status_amount(StatusType.PLUS_COIN_DROP)
                if bonus_check > 0:
                    coin_power -= bonus_check
                    if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                        bonus_sources.append(["Plus Coin Drop", -1*bonus_check])

            else:
                coin_power = 0
        else:
            coin_power = 0
            self.combatant.lower_status_amount(StatusType.PARALYZE)
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Paralyze", 0])

        return [coin_power, is_heads]

    def is_clashing(self):
        # Check to see if clash is possible
        if not (self.opponent.can_act() and self.can_be_clashed and self.opponent.skill_slots[self.targeted_slot].can_be_clashed):
            return False

        # Check if we out-speed and can redirect the skill or if the skill was targeting us in the first place
        if self.combatant.speed > self.opponent.speed or \
           self.opponent.skill_slots[self.targeted_slot].opponent == self.combatant and self.opponent.skill_slots[self.targeted_slot].targeted_slot == self.combatant.skill_slots.index(self) or \
           configs.CLASH_ALWAYS_FORCED:
            return True

        return False

    # Returns a list with the first element being the clash value and the second element being the detailed string
    def get_clash(self):
        bonus_sources = []  # List of Lists. 2nd List is string detailing source name and int of bonus amount
        coins_repeated = [0] * self.coins

        self.combatant.bleed()
        clash_value = self.get_skill_power(bonus_sources)

        coin = 0
        for coin in range(self.coins):
            if self.combatant.coin_flip():
                clash_value += self.get_coin_power(coin, bonus_sources)[0]

        if self.clash_power != 0:
            clash_value += self.clash_power
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                bonus_sources.append(["Clash Power", self.clash_power])


        return [clash_value, bonus_sources]

    def strike(self, clashes=0):
        self.trigger_effect(EffectTrigger.BEFORE_ATTACK)
        total_damage = 0
        coins_repeated = [0]*self.coins

        # Critical Check
        crit_chance = self.combatant.get_status_amount(StatusType.POISE)
        if crit_chance > 0:
            if random.randrange(20) < crit_chance * (2 if self.double_crit_chance else 1) + self.crit_bonus:
                if configs.COMBAT_VERBOSE:
                    print("Critical!")
                self.is_critical = True
                self.combatant.lower_status_count(StatusType.POISE)

        # Strike with each coin
        prev_coin_power = 0
        coin = 0
        while coin < self.coins:
            if self.opponent.hp > 0:
                self.skip_attack = False
                coin_bonus_sources = list()
                self.trigger_coin_effect(EffectTrigger.BEFORE_HIT, coin)
                if not self.skip_attack:
                    coin_flip = self.get_coin_power(coin, coin_bonus_sources)
                    base_value = self.get_skill_power(coin_bonus_sources) + coin_flip[0] + prev_coin_power
                    if prev_coin_power != 0 and configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                        coin_bonus_sources.append(["Previous Coins", prev_coin_power])

                    prev_coin_power += coin_flip[0]
                    phase1_results = self.get_phase1_bonuses(clashes)

                    self.trigger_coin_effect(EffectTrigger.BEFORE_DAMAGE, coin, coin_flip[1])

                    phase3_results = self.get_phase3_bonuses(coin)
                    phase4_results = self.get_phase4_bonuses(coin)

                    damage = math.floor(base_value * (phase1_results[0] / 100) * (phase3_results[0] / 100)) + \
                             phase4_results[0]

                    self.opponent.damage(damage)

                    if configs.COMBAT_VERBOSE:
                        if configs.SHOW_BONUSES:
                            combat_str = f"{self.combatant.sinner.name} rolls {base_value} "
                            if len(coin_bonus_sources) > 0:
                                combat_str += f"({tools.format_sources(coin_bonus_sources)}) "
                            combat_str += f"dealing {damage} damage"
                            if phase1_results[0] != 100 or phase3_results[0] != 100 or phase4_results[0] != 0:
                                combat_str += " ("
                                if phase1_results[0] != 100:
                                    combat_str += f"Phase 1: {phase1_results[0]} ({tools.format_sources(phase1_results[1])}), "
                                if phase3_results[0] != 100:
                                    combat_str += f"Phase 3: {phase3_results[0]} ({tools.format_sources(phase3_results[1])}), "
                                if phase4_results[0] != 0:
                                    combat_str += f"Phase 4: {phase4_results[0]} ({tools.format_sources(phase4_results[1])})"
                                else:
                                    combat_str = combat_str[:-2]
                                combat_str += ")"
                            combat_str += "."
                            print(combat_str)
                        else:
                            print(f"{self.combatant.sinner.name} rolls {base_value} dealing {damage} damage.")

                        # If heads
                        if coin_flip[1]:
                            self.trigger_coin_effect(EffectTrigger.HEADS_HIT, coin, coin_flip[1])
                        else:
                            self.trigger_coin_effect(EffectTrigger.TAILS_HIT, coin, coin_flip[1])

                    for effect in self.effect_on_coin_damage:
                        if effect[0] == coin:
                            if effect[1] == CoinEffect.HEAL:
                                heal_amount = math.floor(damage * (effect[2]/100))
                                self.combatant.heal(heal_amount)
                            elif effect[1] == CoinEffect.RAISE_STAGGER:
                                stagger_amount = math.floor(damage * (effect[2] / 100))
                                self.opponent.add_stagger_offset(stagger_amount)
                            elif effect[1] == CoinEffect.LOWER_OWN_STAGGER:
                                stagger_amount = -1 * math.floor(damage * (effect[2] / 100))
                                self.combatant.add_stagger_offset(stagger_amount)
                            elif effect[1] == CoinEffect.DEAL_PERCENT_DAMAGE:
                                damage_amount = math.floor(damage * (effect[2]/100))
                                if configs.COMBAT_VERBOSE:
                                    print(f"{self.combatant.sinner.name} deals {damage_amount} extra damage.")
                                self.opponent.hp -= damage_amount
                                total_damage += damage_amount

                    total_damage += damage
                else:
                    break

            coin += 1

        if configs.COMBAT_VERBOSE:
            print(f"Total damage is {total_damage}, {self.opponent.sinner.name} is now at {self.opponent.hp} hp.")

    # Returns a List with the first element being the bonus and the second element being a detailed list of sources
    def get_phase1_bonuses(self, clashes):
        # Phase 1 Multiplier Calc
        phase_1_mult = 100
        phase_1_mult_sources = list()

        if self.is_critical:
            phase_1_mult += 20
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                phase_1_mult_sources.append(["Critical", 20])

        resistance = self.opponent.get_resistance(self.skill)
        if resistance != 0:
            phase_1_mult += resistance
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                phase_1_mult_sources.append(["Resistance", resistance])

        def_vs_atk_diff = self.opponent.get_def() - self.combatant.get_off()
        off_vs_def_mult = -1 * math.floor(def_vs_atk_diff / (abs(def_vs_atk_diff) + 25) * 100)
        if off_vs_def_mult != 0:
            phase_1_mult += off_vs_def_mult
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                phase_1_mult_sources.append(["Off vs Def", off_vs_def_mult])

        clash_bonus = clashes * 3
        phase_1_mult += clash_bonus
        if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
            phase_1_mult_sources.append(["Clashes", clash_bonus])

        phase_1_mult = max(phase_1_mult, 0)

        return [phase_1_mult, phase_1_mult_sources]

    # Returns a List with the first element being the bonus and the second element being a detailed list of sources
    def get_phase3_bonuses(self, coin):
        phase_3_mult = 100
        phase_3_mult_sources = list()

        # Check for non-coin status bonuses on attacker
        for status in self.combatant.statuses:
            if (status.type == StatusType.SLASH_DAMAGE_UP and self.skill.type == 0) or \
                    (status.type == StatusType.PIERCE_DAMAGE_UP and self.skill.type == 1) or \
                    (status.type == StatusType.BLUNT_DAMAGE_UP and self.skill.type == 2) or \
                    (status.type == StatusType.DAMAGE_UP):
                phase_3_mult += status.get_amount() * 10
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append([str(status.type), 10 * status.get_amount()])

            elif status.type == StatusType.DAMAGE_DOWN:
                phase_3_mult -= status.get_amount() * 10
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append([str(status.type), -10 * status.get_amount()])

        # Check for non-coin status bonuses on defender
        for status in self.opponent.statuses:
            if (status.type == StatusType.SLASH_FRAGILITY and self.skill.type == 0) or \
                    (status.type == StatusType.PIERCE_FRAGILITY and self.skill.type == 1) or \
                    (status.type == StatusType.BLUNT_FRAGILITY and self.skill.type == 2) or \
                    (status.type == StatusType.FRAGILE):
                phase_3_mult += status.get_amount() * 10
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append([str(status.type), 10 * status.get_amount()])
            elif (status.type == StatusType.SLASH_PROTECTION and self.skill.type == 0) or \
                 (status.type == StatusType.PIERCE_PROTECTION and self.skill.type == 1) or \
                 (status.type == StatusType.BLUNT_PROTECTION and self.skill.type == 2) or \
                 (status.type == StatusType.PROTECTION):
                phase_3_mult -= status.get_amount() * 10
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append([str(status.type), -10 * status.get_amount()])
            elif status.type == StatusType.GAZE and (self.skill.type == 1 or self.skill.type == 2):
                phase_3_mult += status.get_amount() * 20
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append([str(status.type), 20 * status.get_amount()])

        if len(self.phase_3_mult_bonus_sources) > 0:
            phase_3_mult += self.phase_3_mult_bonus
            if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                phase_3_mult_sources += self.phase_3_mult_bonus_sources

        for coin_specific_bonus in self.phase_3_coin_specific:
            if coin_specific_bonus[0] == coin:
                phase_3_mult += coin_specific_bonus[1]
                if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                    phase_3_mult_sources.append(["Skill Effect", coin_specific_bonus[1]])

        return [phase_3_mult, phase_3_mult_sources]

    # Returns a List with the first element being the bonus and the second element being a detailed list of sources
    def get_phase4_bonuses(self, coin):
        phase_4_damage = 0
        phase_4_damage_sources = list()

        # Check for bonus damage from effects on defender
        for status in self.opponent.statuses:
            if status.type == StatusType.RUPTURE or status.type == StatusType.SINKING:
                if status.type == StatusType.SINKING and configs.GAIN_LOSE_SANITY:
                    self.opponent.gain_lose_sp(-1 * status.get_amount())
                else:
                    phase_4_damage += status.get_amount()
                    if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                        phase_4_damage_sources.append([str(status.type), status.get_amount()])

                self.opponent.lower_status_count(status.type)

        for effect in self.effect_on_coin_damage:
            if effect[0] == coin:
                if effect[1] == CoinEffect.PHASE_4_DAMAGE:
                    phase_4_damage += effect[2]
                    if configs.COMBAT_VERBOSE and configs.SHOW_BONUSES:
                        phase_4_damage_sources.append(["Skill Effect", effect[2]])

        return [phase_4_damage, phase_4_damage_sources]

    def trigger_effect(self, trigger: EffectTrigger):
        for effect in self.skill.general_effects:
            if effect.trigger == trigger:
                self.do_effect(effect)

    def trigger_coin_effect(self, trigger: EffectTrigger, coin: int, heads=False):
        if len(self.coin_effects) > coin:
            for effect in self.coin_effects[coin]:
                if effect.trigger == trigger or (effect.trigger == EffectTrigger.ON_HIT and trigger == EffectTrigger.HEADS_HIT) or (effect.trigger == EffectTrigger.ON_HIT and trigger == EffectTrigger.TAILS_HIT):
                    self.do_effect(effect, coin, heads)

    def target_random(self):
        target_selection = self.combatant.team.get_alive_sinners() + self.opponent.team.get_alive_sinners()
        random.shuffle(target_selection)
        self.can_be_clashed = False

        if target_selection[0] != self.combatant:
            return target_selection[0]
        else:
            return target_selection[1]

    def do_effect(self, effect, coin=-1, heads=False):
        conditions_met = True

        for condition in effect.condition:
            if not ((condition.condition == EffectCondition.TARGET_HAS_STATUS_OF_AMOUNT and self.opponent.get_status_amount(condition.condition_status) >= condition.condition_amount) or
                    (condition.condition == EffectCondition.TARGET_HAS_STATUS_OF_COUNT and self.opponent.get_status_count(condition.condition_status) >= condition.condition_amount) or
                    (condition.condition == EffectCondition.TARGET_HAS_LESS_STATUS_OF_AMOUNT and self.opponent.get_status_amount(condition.condition_status) < condition.condition_amount) or
                    (condition.condition == EffectCondition.SPEED_IS_HIGHER and self.combatant.speed > self.opponent.speed) or
                    (condition.condition == EffectCondition.TARGET_ABOVE_HP and (self.opponent.hp / self.opponent.sinner.hp) * 100 > condition.condition_amount) or
                    (condition.condition == EffectCondition.TARGET_BELOW_HP and (self.opponent.hp / self.opponent.sinner.hp) * 100 < condition.condition_amount) or
                    (condition.condition == EffectCondition.SELF_BELOW_HP and (self.combatant.hp / self.combatant.sinner.hp) * 100 < condition.condition_amount) or
                    (condition.condition == EffectCondition.TOOK_NO_DAMAGE_LAST_TURN and not self.combatant.damaged_last_turn) or
                    (condition.condition == EffectCondition.TARGET_TAKEN_DAMAGE and self.opponent.damaged_this_turn) or
                    (condition.condition == EffectCondition.SPEED_AT_LEAST_X and self.combatant.speed >= condition.condition_amount) or
                    (condition.condition == EffectCondition.SELF_HAS_STATUS_OF_AMOUNT and self.combatant.get_status_amount(condition.condition_status) >= condition.condition_amount) or
                    (condition.condition == EffectCondition.SELF_HAS_STATUS_BELOW_COUNT and self.combatant.get_status_count(condition.condition_status) < condition.condition_amount) or
                    (condition.condition == EffectCondition.TOOK_NO_DAMAGE_THIS_TURN and not self.combatant.damaged_this_turn) or
                    (condition.condition == EffectCondition.SPEND_CHARGE and self.combatant.spend_charge(condition.condition_amount)) or
                    (condition.condition == EffectCondition.ON_COIN and coin + 1 == condition.condition_amount) or
                    (condition.condition == EffectCondition.GOT_HEADS and heads) or
                    (condition.condition == EffectCondition.ON_CRIT and self.is_critical) or
                    (condition.condition == EffectCondition.TARGET_HAS_LESS_THAN_SP and self.opponent.sp < condition.condition_amount) or
                    (condition.condition == EffectCondition.SELF_HAS_LESS_THAN_SP and self.combatant.sp < condition.condition_amount) or
                    (condition.condition == EffectCondition.SELF_HAS_MORE_THAN_SP and self.combatant.sp < condition.condition_amount)):
                conditions_met = False
                break

        if conditions_met:
            if effect.effect_detail == EffectDetails.INFLICT_STATUS:
                self.opponent.apply_status(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.GAIN_STATUS:
                self.combatant.apply_status(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.INFLICT_STATUS_NEXT_TURN:
                self.opponent.apply_status_next_turn(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.GAIN_STATUS_NEXT_TURN:
                self.combatant.apply_status_next_turn(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.APPLY_STATUS_COUNT:
                self.opponent.raise_status_count(effect.status, effect.amount)
            elif effect.effect_detail == EffectDetails.GAIN_STATUS_COUNT:
                self.combatant.raise_status_count(effect.status, effect.amount)
            elif effect.effect_detail == EffectDetails.APPLY_STATUS_COUNT_NEXT_TURN:
                self.opponent.raise_status_count_next_turn(effect.status, effect.amount)
            elif effect.effect_detail == EffectDetails.GAIN_STATUS_COUNT_NEXT_TURN:
                self.combatant.raise_status_count_next_turn(effect.status, effect.amount)
            elif effect.effect_detail == EffectDetails.RAISE_ATTACK_DAMAGE_MULT:
                self.phase_3_mult_bonus += effect.amount
                self.phase_3_mult_bonus_sources.append(["Skill Effect", effect.amount])
            elif effect.effect_detail == EffectDetails.COIN_DMG_MULT:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.phase_3_coin_specific.append([coin, effect.amount])
            elif effect.effect_detail == EffectDetails.COIN_POWER:
                self.coin_power_bonus += effect.amount
            elif effect.effect_detail == EffectDetails.HEAL_FOR_DAMAGE:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.effect_on_coin_damage.append([coin, CoinEffect.HEAL, effect.amount])
            elif effect.effect_detail == EffectDetails.ADDED_DAMAGE:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.effect_on_coin_damage.append([coin, CoinEffect.PHASE_4_DAMAGE, effect.amount])
            elif effect.effect_detail == EffectDetails.RAISE_STAGGER_BY_DAMAGE:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.effect_on_coin_damage.append([coin, CoinEffect.RAISE_STAGGER, effect.amount])
            elif effect.effect_detail == EffectDetails.LOWER_SELF_STAGGER_BY_DAMAGE:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.effect_on_coin_damage.append([coin, CoinEffect.LOWER_OWN_STAGGER, effect.amount])
            elif effect.effect_detail == EffectDetails.DEAL_PERCENT_BONUS_DAMAGE:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.effect_on_coin_damage.append([coin, CoinEffect.DEAL_PERCENT_DAMAGE, effect.amount])
            elif effect.effect_detail == EffectDetails.RAISE_NEXT_COIN:
                if coin == -1:
                    print("Warning: Coin specific trigger not assigned to a coin.")
                else:
                    self.specific_coin_power_bonus.append([coin + 1, effect.amount])
            elif effect.effect_detail == EffectDetails.BOOST_STATUS_OF_FUTURE_COIN:
                self.status_boost += effect.amount
            elif effect.effect_detail == EffectDetails.GIVE_STATUS_TO_LOWEST_ALLY:
                target = self.combatant.team.get_lowest_hp()
                if target is not None:
                    target.apply_status(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.GIVE_STATUS_TO_SLOWEST_ALLY:
                target = self.combatant.team.get_slowest()
                if target is not None:
                    target.apply_status(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.SKILL_POWER:
                self.skill_power_bonus += effect.amount
            elif effect.effect_detail == EffectDetails.BURST_TREMOR:
                if configs.USE_STAGGER:
                    tremor = self.opponent.get_status_amount(StatusType.TREMOR)
                    if tremor > 0:
                        self.opponent.add_stagger_offset(tremor)
                        if configs.COMBAT_VERBOSE:
                            print(f"{self.combatant.sinner.name} bursts {tremor} tremor. {self.opponent.sinner.name}'s new threshold is {self.opponent.get_stagger_threshold()}")
            elif effect.effect_detail == EffectDetails.APPLY_STATUS_TO_RANDOM_ENEMIES:
                random_enemies = self.opponent.team.get_random(2)
                for enemy in random_enemies:
                    enemy.apply_status(Status(effect.status, effect.amount + self.status_boost))
            elif effect.effect_detail == EffectDetails.REPEAT_COIN:
                if self.skill.coin_effects[effect.amount-1] in self.coin_effects:
                    self.coin_effects.insert(self.coin_effects.index(self.skill.coin_effects[effect.amount-1])+1, self.skill.coin_effects[effect.amount-1])
                    self.coins += 1
            elif effect.effect_detail == EffectDetails.SPEND_AMMO:
                if self.combatant.ammo >= effect.amount:
                    self.combatant.ammo -= effect.amount
                    if configs.COMBAT_VERBOSE:
                        print(f"Spent 1 Ammo, {self.combatant.ammo} ammo left.")
                else:
                    self.skip_attack = True
                    if configs.COMBAT_VERBOSE:
                        print(f"{self.combatant.sinner.name} is out of ammo.")
            elif effect.effect_detail == EffectDetails.LOSE_HP:
                self.combatant.hp -= effect.amount
                if configs.COMBAT_VERBOSE:
                    print(f"{self.combatant.sinner.name} self inflicts {effect.amount} damage.")
            elif effect.effect_detail == EffectDetails.DOUBLE_CRIT_CHANCE:
                self.double_crit_chance = True
            elif effect.effect_detail == EffectDetails.TARGET_RANDOM:
                self.target_random()
            elif effect.effect_detail == EffectDetails.REMOVE_STATUS:
                self.combatant.remove_status(effect.status)
            elif effect.effect_detail == EffectDetails.LOSE_PERCENT_HP:
                damage_amount = math.floor(self.combatant.hp * effect.amount)
                self.combatant.hp -= damage_amount
                if configs.COMBAT_VERBOSE:
                    print(f"{self.combatant} hurts themself for {damage_amount}")
            elif effect.effect_detail == EffectDetails.NEG_SP_TO_CRIT:
                self.crit_bonus += abs(min(self.opponent.sp, 0))
            elif effect.effect_detail == EffectDetails.HEAL_SP:
                if configs.GAIN_LOSE_SANITY:
                    self.combatant.gain_lose_sp(effect.amount)
            elif effect.effect_detail == EffectDetails.TARGET_LOSE_SP:
                if configs.GAIN_LOSE_SANITY:
                    self.opponent.gain_lose_sp(-1 * effect.amount)
            elif effect.effect_detail == EffectDetails.REDUCE_CLASH_POWER:
                self.opponent.skill_slots[self.targeted_slot].clash_power -= effect.amount
            else:
                print("Warning: Skill effect not implemented.")


class Effect(typing.NamedTuple):
    trigger: EffectTrigger
    effect_detail: EffectDetails
    amount: int
    other: typing.Optional[int] = 0
    condition: typing.Optional[list] = list()
    status: typing.Optional[StatusType] = None


class Condition(typing.NamedTuple):
    condition: EffectCondition
    condition_amount: typing.Optional[int] = 1
    condition_status: typing.Optional[StatusDef] = None
