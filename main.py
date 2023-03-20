# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import copy
import math
import random
import typing
from enum import Enum

# Configs
USE_RESISTANCE = False
FIRST_TO_X_WINS = 25  # 2 = Best of 3, 5 = Best of 9


class EffectCondition(Enum):
    ON_HIT = 0
    ON_HEAD = 1
    ClASH_WIN = 2
    ON_USE = 3
    COMBAT_START = 4
    TARGET_TAKEN_DAMAGE = 5
    TARGET_HAS_STATUS_OF_AMOUNT = 6
    SPEED_IS_HIGHER = 7
    TARGET_ABOVE_HP = 8
    TOOK_NO_DAMAGE_LAST_TURN = 9


class EffectDetails(Enum):
    APPLY_STATUS = 100
    APPLY_STATUS_ON_SELF = 101
    APPLY_STATUS_NEXT_TURN = 102
    APPLY_STATUS_NEXT_TURN_ON_SELF = 103
    RAISE_STATUS_COUNT = 104
    RAISE_ATTACK_DAMAGE_MULT = 105
    COIN_HIT_MULT = 106
    COIN_POWER = 107
    HEAL_FOR_DAMAGE = 108
    RAISE_NEXT_COIN = 109


class StatusType(Enum):
    def __str__(self):
        match self.value:
            case 200:
                return "Sinking"
            case 201:
                return "Rupture"
            case 202:
                return "Attack Power Up"
            case 203:
                return "Poise"
            case 204:
                return "Slash DMG Up"
            case 205:
                return "Pierce DMG Up"
            case 206:
                return "Blunt DMG Up"
            case 207:
                return "Bleed"
            case 208:
                return "Haste"
            case 209:
                return "Tremor"
            case 210:
                return "Defense Level Up"
            case 211:
                return "Protection"
            case 212:
                return "Attack Power Down"
            case 213:
                return "Defense Power Down"
            case 214:
                return "Slash Fragility"
            case 215:
                return "Pierce Fragility"
            case 216:
                return "Blunt Fragility"
            case 217:
                return "Damage Up"
            case 218:
                return "Paralysis"
            case 219:
                return "Offense Level Down"
            case _:
                return "Can Not Find: " + str(self)

    SINKING = 200
    RUPTURE = 201
    ATTACK_POWER = 202
    POISE = 203
    SLASH_DAMAGE_UP = 204
    PIERCE_DAMAGE_UP = 205
    BLUNT_DAMAGE_UP = 206
    BLEED = 207
    HASTE = 208
    TREMOR = 209
    DEFENSE_LEVEL_UP = 210
    PROTECTION = 211
    ATTACK_POWER_DOWN = 212
    DEFENSE_POWER_DOWN = 213 # TODO: Implement Defense Power Down
    SLASH_FRAGILITY = 214
    PIERCE_FRAGILITY = 215
    BLUNT_FRAGILITY = 216
    DAMAGE_UP = 217
    PARALYSIS = 218
    OFFENSE_LEVEL_DOWN = 219


class Effect(typing.NamedTuple):
    condition: EffectCondition
    effect_detail: EffectDetails
    amount: int
    other: typing.Optional[int] = 0
    conditional_amount: typing.Optional[int] = 0
    conditional_status: typing.Optional[StatusType] = None
    status: typing.Optional[StatusType] = None


class Skill(typing.NamedTuple):
    name: str
    type: int  # 0=Slash, 1=Pierce, 2=Blunt
    base: int
    coin_bonus: int
    coin_num: int
    general_effects: list
    coin_effects: list


class Sinner(typing.NamedTuple):
    name: str
    hp: int
    spd_min: int
    spd_max: int
    def_base: int
    off_base: int
    res: list
    skills: list


class Status:
    def __init__(self, status: StatusType, amount, count=1):
        self.type = status
        self.amount = amount
        self.count = count

    type: StatusType
    amount: int
    count: int = 1


class CombatStats:
    def __init__(self, sinner):
        self.sinner = sinner
        self.hp = sinner.hp
        self.status = []
        self.status_next_turn = []
        self.combat_deck = []
        self.status_count_next_turn = []
        self.speed = 0

    sinner = None
    hp = 0
    status: list
    status_next_turn: list
    status_count_next_turn: list
    combat_deck: list
    damaged_this_turn = False
    damaged_last_turn = False
    speed: int

    def get_off(self):
        return self.sinner.off_base - self.get_status_amount(StatusType.OFFENSE_LEVEL_DOWN)

    def get_def(self):
        return self.sinner.def_base + self.get_status_amount(StatusType.DEFENSE_LEVEL_UP)

    def remove_status(self, status_to_remove: StatusType):
        for status in self.status:
            if status.type == status_to_remove:
                self.status.remove(status)

                return

    def lower_status_count(self, status_to_lower: StatusType):
        status_found = False
        new_count = 0

        for status in self.status:
            if status.type == status_to_lower:
                status.count -= 1
                new_count = status.count

                if status.count == 0:
                    self.status.remove(status)

                status_found = True

        if status_found:
            print(f"{self.sinner.name}'s {status_to_lower}'s count lowered by 1 (now {new_count})")

    def raise_status_count(self, status_to_raise: StatusType, count: int):
        status_not_found = True
        new_count = count

        for status in self.status:
            if status.type == status_to_raise:
                if not status_not_found:
                    print(f"Warning: Duplicate status {status_to_raise} found on {self.sinner.name}")

                status.count += count
                new_count = status.count

                status_not_found = False

        if status_not_found:
            self.status.append(Status(status_to_raise, 1, count=count))

        print(f"{self.sinner.name}'s {status_to_raise} gains {count} count (now {new_count})")

    def apply_status(self, status: Status):
        print(f"{self.sinner.name} gains {status.type} ({status.count}, {status.amount})")
        status_not_found = True
        for checked_status in self.status:
            if status.type == checked_status.type:
                if not status_not_found:
                    print(f"Warning: Duplicate status {status.type} found on {self.sinner.name}")

                checked_status.amount += status.amount
                status_not_found = False
                break

        if status_not_found:
            self.status.append(copy.copy(status))

    def apply_status_next_turn(self, status: Status):
        self.status_next_turn.append(status)

    def raise_status_count_next_turn(self, status_to_raise: StatusType, count: int):
        self.status_count_next_turn.append([status_to_raise, count])

    def end_of_turn(self):
        self.remove_status(StatusType.ATTACK_POWER)
        self.remove_status(StatusType.HASTE)
        self.remove_status(StatusType.PROTECTION)
        self.remove_status(StatusType.DEFENSE_LEVEL_UP)
        self.remove_status(StatusType.ATTACK_POWER_DOWN)
        self.remove_status(StatusType.DEFENSE_POWER_DOWN)
        self.remove_status(StatusType.SLASH_DAMAGE_UP)
        self.remove_status(StatusType.BLUNT_DAMAGE_UP)
        self.remove_status(StatusType.PIERCE_DAMAGE_UP)
        self.remove_status(StatusType.SLASH_FRAGILITY)
        self.remove_status(StatusType.BLUNT_FRAGILITY)
        self.remove_status(StatusType.PIERCE_FRAGILITY)
        self.remove_status(StatusType.DAMAGE_UP)
        self.remove_status(StatusType.OFFENSE_LEVEL_DOWN)
        self.lower_status_count(StatusType.POISE)

        for status in self.status_next_turn:
            self.apply_status(status)

        for status in self.status_count_next_turn:
            self.raise_status_count(status[0], status[1])

        self.status_next_turn = []
        self.status_count_next_turn = []

        self.damaged_last_turn = self.damaged_this_turn
        self.damaged_this_turn = False

    def get_status_amount(self, status_type: StatusType):
        for status in self.status:
            if status.type == status_type:
                return status.amount

        return 0

    def get_status_count(self, status_type: StatusType):
        for status in self.status:
            if status.type == status_type:
                return status.count

        return 0

    def speed_roll(self):
        self.speed = random.randrange(self.sinner.spd_min, self.sinner.spd_max+1) + self.get_status_amount(StatusType.HASTE)


def format_sources(sources):
    source_info = ""
    for source in sources:
        source_info += f"{source[0]}: "
        if source[1] >= 0:
            source_info += "+"
        source_info += str(source[1]) + ", "

    return source_info[:-2]


def combat(fighting_sinners):
    combatants = [CombatStats(fighting_sinners[0]),
                  CombatStats(fighting_sinners[1])]

    print(combatants[0].sinner.name + " vs " + combatants[1].sinner.name + "\n")

    while combatants[0].hp > 0 and combatants[1].hp > 0:
        skills_used = [-1, -1]
        i = 0
        for combatant in combatants:
            combatant.speed_roll()

            if len(combatant.combat_deck) < 2:
                new_deck = [0, 0, 0, 1, 1, 2]
                random.shuffle(new_deck)
                combatant.combat_deck += new_deck

            skills_used[i] = max(combatant.combat_deck[0], combatant.combat_deck[1])
            combatant.combat_deck.remove(skills_used[i])
            i += 1

        clash(combatants[0], skills_used[0], combatants[1], skills_used[1])
        for combatant in combatants:
            combatant.end_of_turn()

    if combatants[0].hp > 0:
        winner = 0
        loser = 1
    else:
        winner = 1
        loser = 0

    print(f"{combatants[winner].sinner.name} beats {combatants[loser].sinner.name} with {combatants[winner].hp}"
          f" hp remaining.")

    return winner


def clash(combatant1, skill1_num, combatant2, skill2_num):
    combatants_info = [combatant1, combatant2]
    skills = [combatant1.sinner.skills[skill1_num], combatant2.sinner.skills[skill2_num]]
    combatants_coins = [skills[0].coin_num, skills[1].coin_num]
    bonus_coin_value = [0,0]
    bonus_skill_value = [0,0]
    combatant_phase_3_mult = [0, 0]

    print(f"{combatant1.sinner.name} (speed {combatant1.speed}) using {skills[0].name} ({skills[0].base} +{skills[0].coin_bonus}) vs "
          f"{combatant2.sinner.name} (speed {combatant2.speed}) using {skills[1].name} ({skills[1].base} +{skills[1].coin_bonus})")

    clashes = 0

    # Check on Use Skills
    for combatant in range(2):
        for effect in skills[combatant].general_effects:
            if effect.condition == EffectCondition.ON_USE or effect.condition == EffectCondition.COMBAT_START or \
                    (effect.condition == EffectCondition.TARGET_ABOVE_HP and (
                            combatants_info[(combatant + 1) % 2].hp / combatants_info[
                        (combatant + 1) % 2].sinner.hp) * 100 > effect.conditional_amount) or \
                    (effect.condition == EffectCondition.TOOK_NO_DAMAGE_LAST_TURN and not combatants_info[
                        combatant].damaged_last_turn):
                if effect.effect_detail == EffectDetails.RAISE_ATTACK_DAMAGE_MULT:
                    combatant_phase_3_mult[combatant] += effect.amount
                elif effect.effect_detail == EffectDetails.APPLY_STATUS:
                    combatants_info[(combatant + 1) % 2].apply_status(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_ON_SELF:
                    combatants_info[combatant].apply_status(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.RAISE_STATUS_COUNT:
                    combatants_info[(combatant + 1) % 2].raise_status_count(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN:
                    combatants_info[(combatant + 1) % 2].apply_status_next_turn(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF:
                    combatants_info[combatant].apply_status_next_turn(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.COIN_POWER:
                    bonus_coin_value[combatant] += effect.amount
                else:
                    print("Warning: Effect not used " + str(effect.effect_detail))

        for status in combatants_info[combatant].status:
            if status.type == StatusType.ATTACK_POWER:
                bonus_skill_value[combatant] += status.amount
            if status.type == StatusType.ATTACK_POWER_DOWN:
                bonus_skill_value[combatant] -= status.amount

    attack_diff = abs(combatants_info[0].get_off() - combatants_info[1].get_off()) // 5

    print(f"{combatants_info[0].get_off()} vs {combatants_info[1].get_off()}")
    while combatants_coins[0] > 0 and combatants_coins[1] > 0:
        clashes += 1
        print("Clash " + str(clashes) + ": " + str(combatants_coins[0]) + " coins vs " +
              str(combatants_coins[1]) + " coins")

        clash_values = [0, 0]
        heads = [0, 0]

        combat_str = ""

        for combatant in range(2):
            clash_values[combatant] = skills[combatant].base + bonus_skill_value[combatant]
            heads[combatant] = 0

            bleed = combatants_info[combatant].get_status_amount(StatusType.BLEED)
            if bleed > 0:
                combatants_info[combatant].hp -= bleed
                combatants_info[combatant].lower_status_count(StatusType.BLEED)
                print(f"{combatants_info[combatant].sinner.name} has taken {bleed} bleed damage.")

            for coin in range(combatants_coins[combatant]):
                if coin_flip():
                    heads[combatant] += 1
                    clash_values[combatant] += skills[combatant].coin_bonus + bonus_coin_value[combatant]

            if ((combatants_info[0].get_off() > combatants_info[1].get_off() and combatant == 0) or
                (combatants_info[0].get_off() < combatants_info[1].get_off()) and combatant == 1) and attack_diff > 0:
                clash_values[combatant] += abs(attack_diff)
                off_change = True
            else:
                off_change = False

            combat_str += str(clash_values[combatant]) + " (" + str(heads[combatant]) + " head"
            if off_change:
                combat_str += ", offense +" + str(abs(attack_diff))
            if bonus_coin_value[combatant] > 0:
                combat_str += ", coin value +" + str(bonus_coin_value[combatant])
            combat_str += ")"

            if combatant == 0:
                combat_str += " vs "

        print(combat_str)

        if clash_values[0] > clash_values[1]:
            combatants_coins[1] -= 1
            print(combatants_info[0].sinner.name + " wins clash")
        elif clash_values[1] > clash_values[0]:
            combatants_coins[0] -= 1
            print(combatants_info[1].sinner.name + " wins clash")
        else:
            print("Draw")

    if combatants_info[0].hp > 0 and combatants_info[1].hp > 0:
        if combatants_coins[0] > 0:
            attacker = 0
            defender = 1
        else:
            attacker = 1
            defender = 0
    
        coin_values = []
        total_base_damage = 0
        base_damage_sources = []
        phase_1_mult = 100
        phase_1_mult_sources = []
        phase_3_mult = 100 + combatant_phase_3_mult[attacker]
        phase_3_mult_sources = []
        phase_3_coin_specific = []
        phase_4_damage = 0
        phase_4_damage_sources = []
        heads = 0
        coin_heal = []
        is_critical = False
    
        # Check for clash win skills or have effect on damage
        for effect in skills[attacker].general_effects:
            if effect.condition == EffectCondition.ClASH_WIN:
                if effect.effect_detail == EffectDetails.RAISE_ATTACK_DAMAGE_MULT:
                    phase_3_mult += effect.amount
                elif effect.effect_detail == EffectDetails.APPLY_STATUS:
                    combatants_info[defender].apply_status(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_ON_SELF:
                    combatants_info[attacker].apply_status(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.RAISE_STATUS_COUNT:
                    combatants_info[attacker].raise_status_count(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN:
                    combatants_info[defender].apply_status_next_turn(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF:
                    combatants_info[attacker].apply_status_next_turn(Status(effect.status, effect.amount))
                elif effect.effect_detail == EffectDetails.COIN_POWER:
                    bonus_coin_value[attacker] += effect.amount
                else:
                    print("Warning: Effect not used " + str(effect.effect_detail))
    
        # Critical Check
        crit_chance = combatants_info[attacker].get_status_amount(StatusType.POISE) * 5
        if random.randrange(100) < crit_chance:
            is_critical = True
            combatants_info[attacker].lower_status_count(StatusType.POISE)
            phase_1_mult += 20
            phase_1_mult_sources.append(["Critical", 20])

        next_coin_boost = [0] * combatants_coins[attacker]
        for coin in range(combatants_coins[attacker]):
            status_to_apply = []
            status_to_apply_to_self = []
            status_to_count_increase = []
            bonus_base_damage = 0
    
            if coin_flip():
                heads += 1
                got_head = True
            else:
                got_head = False
    
            # Check for coin bonuses
            if len(skills[attacker].coin_effects) > coin:
                for effect in skills[attacker].coin_effects[coin]:
                    # Skills that happen after the hit
                    if effect.condition == EffectCondition.ON_HIT or \
                            (effect.condition == EffectCondition.ON_HEAD and got_head):
                        if effect.effect_detail == EffectDetails.APPLY_STATUS:
                            status_not_found = True
    
                            for status in status_to_apply:
                                if status.type == effect.status:
                                    status.amount += effect.amount
                                    status_not_found = False
                                    break
    
                            if status_not_found:
                                status_to_apply.append(Status(effect.status, effect.amount))
    
                        elif effect.effect_detail == EffectDetails.APPLY_STATUS_ON_SELF:
                            status_not_found = True
    
                            for status in status_to_apply_to_self:
                                if status.type == effect.status:
                                    status.amount += effect.amount
                                    status_not_found = False
                                    break
    
                            if status_not_found:
                                status_to_apply_to_self.append(Status(effect.status, effect.amount))
                        elif effect.effect_detail == EffectDetails.RAISE_STATUS_COUNT:
                            status_to_count_increase.append([effect.status, effect.amount])
                        elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN:
                            combatants_info[defender].apply_status_next_turn(Status(effect.status, effect.amount))
                        elif effect.effect_detail == EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF:
                            combatants_info[attacker].apply_status_next_turn(Status(effect.status, effect.amount))
                        elif effect.effect_detail == EffectDetails.HEAL_FOR_DAMAGE:
                            coin_heal.append([coin, effect.amount])
                        elif effect.effect_detail == EffectDetails.RAISE_NEXT_COIN:
                            if coin+1 <= combatants_coins[attacker]-1:
                                next_coin_boost[coin+1] += effect.amount
                        else:
                            print("Warning: Unsupported Effect " + str(effect))
    
                    # Skills that happen before the hit
                    elif (effect.condition == EffectCondition.TARGET_TAKEN_DAMAGE and combatants_info[defender].damaged_this_turn) or \
                         (effect.condition == EffectCondition.TARGET_HAS_STATUS_OF_AMOUNT and combatants_info[defender].get_status_amount(effect.conditional_status) >= effect.conditional_amount) or \
                         (effect.condition == EffectCondition.SPEED_IS_HIGHER and combatants_info[attacker].speed > combatants_info[defender].speed):
                        if effect.effect_detail == EffectDetails.COIN_HIT_MULT:
                            phase_3_coin_specific.append([coin, effect.amount])
                            phase_3_mult_sources.append([f"Coin {coin + 1} Multiplier", effect.amount])
                        else:
                            print("Warning: Unsupported Effect " + str(effect))
    
    
            # Check for bonus damage from effects on defender
            for status in combatants_info[defender].status:
                if status.type == StatusType.SINKING or status.type == StatusType.RUPTURE:
                    phase_4_damage_sources.append([str(StatusType(status.type)), status.amount])
                    phase_4_damage += status.amount
    
                    combatants_info[defender].lower_status_count(status.type)

            # Check for bonus damage from statuses on attacker
            for status in combatants_info[attacker].status:
                if status.type == StatusType.ATTACK_POWER:
                    bonus_base_damage += status.amount
                    base_damage_sources.append([str(status.type), status.amount])
                elif status.type == StatusType.ATTACK_POWER_DOWN:
                    bonus_base_damage -= status.amount
                    base_damage_sources.append([str(status.type), -1 * status.amount])
    
            coin_damage_base = skills[attacker].base + heads * (skills[attacker].coin_bonus + bonus_coin_value[attacker]) + bonus_base_damage + next_coin_boost[coin]
            coin_values.append(coin_damage_base)
            total_base_damage += coin_damage_base
    
            previous_heads = heads - int(got_head)
            base_damage_sources.append(["Skill Base", skills[attacker].base])
            if got_head:
                base_damage_sources.append(["Head", skills[attacker].coin_bonus])
            if previous_heads > 0:
                base_damage_sources.append(["Previous Heads", previous_heads * skills[attacker].coin_bonus])
    
            for status in status_to_apply:
                combatants_info[defender].apply_status(status)
    
            for status in status_to_apply_to_self:
                combatants_info[attacker].apply_status(status)
    
            for status in status_to_count_increase:
                combatants_info[defender].raise_status_count(status[0], status[1])
    
            combatants_info[defender].damaged_this_turn = True

        # Check for non-coin status bonuses on attacker
        for status in combatants_info[attacker].status:
            if (status.type == StatusType.SLASH_DAMAGE_UP and skills[attacker].type == 0) or \
               (status.type == StatusType.PIERCE_DAMAGE_UP and skills[attacker].type == 1) or \
               (status.type == StatusType.BLUNT_DAMAGE_UP and skills[attacker].type == 2) or \
               (status.type == StatusType.DAMAGE_UP):
                phase_3_mult_sources.append([str(StatusType(status.type)), 10 * status.amount])
                phase_3_mult += status.amount * 10

        # Check for non-coin status bonuses on attacker
        for status in combatants_info[defender].status:
            if (status.type == StatusType.SLASH_FRAGILITY and skills[attacker].type == 0) or \
                 (status.type == StatusType.PIERCE_FRAGILITY and skills[attacker].type == 1) or \
                 (status.type == StatusType.BLUNT_FRAGILITY and skills[attacker].type == 2):
                phase_3_mult_sources.append([str(StatusType(status.type)), 10 * status.amount])
                phase_3_mult += status.amount * 10


    
        if USE_RESISTANCE:
            phase_1_mult += combatants_info[defender].sinner.res[skills[attacker].type]
            phase_1_mult_sources.append((["Resistance", combatants_info[defender].sinner.res[skills[attacker].type]]))
    
        # calculate damage bonus for attack vs defense
        def_vs_atk_diff = combatants_info[defender].get_def() - combatants_info[attacker].get_off()
        phase_1_off_vs_def = math.floor(def_vs_atk_diff / (abs(def_vs_atk_diff) + 25) * 100)
        phase_1_mult -= phase_1_off_vs_def
        phase_1_mult_sources.append(["Offense vs Defense", phase_1_off_vs_def*-1])
        phase_1_clash_bonus = clashes * 3
        phase_1_mult += phase_1_clash_bonus
        phase_1_mult_sources.append(["Clash Bonus", phase_1_clash_bonus])
    
        phase_1_mult = max(phase_1_mult, 0)

        protection = 10 * combatants_info[defender].get_status_amount(StatusType.PROTECTION)
        if protection > 0:
            phase_3_mult -= protection
            phase_3_mult_sources.append(["Protection", -1 * protection])
    
        damage = 0
        coin_damages_str = []
    
        coin_iterator = 0
        for coin_value in coin_values:
            coin_specific_mult = 0
            for mult in phase_3_coin_specific:
                if mult[0] == coin_iterator:
                    coin_specific_mult += mult[1]
    
            calc_damage = math.floor(coin_value * (phase_1_mult / 100) * ((phase_3_mult + coin_specific_mult) / 100))
            damage += calc_damage
            coin_damages_str.append(str(calc_damage))

            for heal in coin_heal:
                if heal[0] == coin_iterator:
                    heal_amount = math.floor(calc_damage * (heal[1]/100))
                    combatants_info[attacker].hp += heal_amount
                    print(f"{combatants_info[attacker].sinner.name} healed for {heal_amount}")

            coin_iterator += 1
    
        damage += phase_4_damage
    
        combatants_info[defender].hp -= damage
    
        print(f"{combatants_info[attacker].sinner.name} deals {damage} damage to {combatants_info[defender].sinner.name}, ("
              f"{combatants_info[defender].hp} hp remaining)")
    
        print(f"Damage from each hit: {' + '.join(coin_damages_str)}")
        print(f"Total Base Damage: {total_base_damage} ({format_sources(base_damage_sources)})")
        if phase_1_mult != 100:
            print(f"Phase 1 Mult: {phase_1_mult} ({format_sources(phase_1_mult_sources)})")
        if phase_3_mult != 100 or len(phase_3_coin_specific) > 0:
            print(f"Phase 3 Mult: {phase_3_mult} ({format_sources(phase_3_mult_sources)})")
        if phase_4_damage != 0:
            print(f"Phase 4 Bonus: {phase_4_damage} ({format_sources(phase_4_damage_sources)})")
    
        print("")


def coin_flip():
    return random.randrange(2) == 1


sinners = {
    "LCB_Sinner_Yi_Sang": Sinner("LCB Sinner Yi Sang", 147, 4, 8, 36, 28, [50, -25, 0],
                                 [Skill("Deflect", 0, 3, 7, 1, [], [[Effect(EffectCondition.ON_HEAD, EffectDetails.APPLY_STATUS, 2, status=StatusType.SINKING)]]),
                                  Skill("End-stop Stab", 1, 4, 4, 2, [], [[], [Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.SINKING),
                                                                               Effect(EffectCondition.ON_HIT, EffectDetails.RAISE_STATUS_COUNT, 1, status=StatusType.SINKING)]]),
                                  Skill("Enjamb", 0, 6, 1, 3, [], [])]),  # TODO: Implement SP Effect
    "LCB_Sinner_Sinclair": Sinner("LCB Sinner Sinclair", 121, 3, 7, 26, 38, [-25, 50, 0],
                                  [Skill("Downward Swing", 0, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.RUPTURE)]]),
                                   Skill("Halberd Combo", 1, 4, 2, 3, [Effect(EffectCondition.ClASH_WIN, EffectDetails.RAISE_ATTACK_DAMAGE_MULT, 30)], []),
                                   Skill("Ravaging Cut", 0, 5, 2, 3, [Effect(EffectCondition.ClASH_WIN, EffectDetails.APPLY_STATUS_ON_SELF, 1, status=StatusType.ATTACK_POWER)], [])]),
    "LCB_Sinner_Ryoshu": Sinner("LCB Sinner Ryoshu", 134, 3, 6, 28, 36, [-25, 0, 50],
                                  [Skill("Paint", 0, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 2, status=StatusType.POISE)]]),
                                   Skill("Splatter", 0, 4, 4, 2, [], [[Effect(EffectCondition.TARGET_TAKEN_DAMAGE, EffectDetails.COIN_HIT_MULT, 30)],
                                                                      [Effect(EffectCondition.TARGET_TAKEN_DAMAGE, EffectDetails.COIN_HIT_MULT, 30)]]),
                                   Skill("Brushstroke", 0, 5, 2, 3, [Effect(EffectCondition.COMBAT_START, EffectDetails.APPLY_STATUS_ON_SELF, 2, status=StatusType.SLASH_DAMAGE_UP)], [])]),
    "LCB_Sinner_Rodion": Sinner("LCB Sinner Rodion", 159, 2, 5, 31, 33, [-25, 50, 0],
                                  [Skill("Strike Down", 0, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.BLEED)]]),
                                   Skill("Axe Combo", 0, 4, 4, 2, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.BLEED)],
                                                                       [Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.BLEED)]]),
                                   Skill("Slay", 0, 2, 2, 4, [], [[], [], [], [Effect(EffectCondition.TARGET_HAS_STATUS_OF_AMOUNT, EffectDetails.COIN_HIT_MULT, 20, conditional_status=StatusType.BLEED, conditional_amount=6)]])]),  # TODO: Implement SP Effect
    "LCB_Sinner_Outis": Sinner("LCB Sinner Outis", 120, 3, 7, 26, 38, [-25, 0, 50],
                                  [Skill("Pulled Blade", 1, 3, 2, 3, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.RUPTURE)]]),
                                   Skill("Backslash", 0, 4, 4, 2, [], [[Effect(EffectCondition.SPEED_IS_HIGHER, EffectDetails.COIN_HIT_MULT, 20)],
                                                                       [Effect(EffectCondition.SPEED_IS_HIGHER, EffectDetails.COIN_HIT_MULT, 20)]]),
                                   Skill("Piercing Thrust", 1, 6, 14, 1, [Effect(EffectCondition.TARGET_ABOVE_HP, EffectDetails.RAISE_ATTACK_DAMAGE_MULT, 20, conditional_amount=50)], [])]),
    "LCB_Sinner_Meursault": Sinner("LCB Sinner Meursault", 184, 2, 3, 38, 26, [0, 50, -25],
                                  [Skill("Un, Deux", 2, 2, 4, 2, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.TREMOR)]]),
                                   Skill("Nailing Fist", 2, 5, 8, 1, [Effect(EffectCondition.ON_USE, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 3, status=StatusType.DEFENSE_LEVEL_UP)], []),
                                   Skill("Des Coups", 2, 4, 1, 4, [Effect(EffectCondition.ON_USE, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 3, status=StatusType.PROTECTION)],  # TODO: Burst Tremor
                                         [[], [], [], [Effect(EffectCondition.ON_HIT, EffectDetails.RAISE_STATUS_COUNT, 2, status=StatusType.TREMOR)]])]),
    "LCB_Sinner_Ishmael": Sinner("LCB Sinner Ishmael", 159, 5, 8, 33, 31, [50, 0, -25],
                                  [Skill("Loggerhead", 2, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.RAISE_STATUS_COUNT, 1, status=StatusType.TREMOR)]]),
                                   Skill("Slide", 2, 5, 8, 1, [Effect(EffectCondition.ClASH_WIN, EffectDetails.APPLY_STATUS, 3, status=StatusType.DEFENSE_POWER_DOWN)], []),
                                   Skill("Guard", 2, 7, 12, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 1, status=StatusType.BLUNT_FRAGILITY)]])]),  # TODO: Burst Tremor
    "LCB_Sinner_Hong_Lu": Sinner("LCB Sinner Hong Lu", 134, 3, 6, 28, 36, [50, 0, -25],
                                  [Skill("Downward Cleave", 2, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.SINKING)]]),
                                   Skill("Dual Strike", 0, 4, 4, 2, [Effect(EffectCondition.TOOK_NO_DAMAGE_LAST_TURN, EffectDetails.COIN_POWER, 1)],
                                         [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 1, status=StatusType.SINKING)],
                                          [Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 2, status=StatusType.RUPTURE)]]),
                                   Skill("Whirlwind", 2, 5, 4, 2, [Effect(EffectCondition.TOOK_NO_DAMAGE_LAST_TURN, EffectDetails.COIN_POWER, 2)],
                                         [[], [Effect(EffectCondition.ON_HEAD, EffectDetails.APPLY_STATUS, 2, status=StatusType.ATTACK_POWER_DOWN)]])]),
    "LCB_Sinner_Heathcliff": Sinner("LCB Sinner Heathcliff", 159, 2, 5, 31, 33, [50, 0, -25],
                                  [Skill("Bat Bash", 2, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 3, status=StatusType.TREMOR)]]),
                                   Skill("Smackdown", 2, 4, 4, 2, [Effect(EffectCondition.ON_USE, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 1, status=StatusType.ATTACK_POWER),
                                                                   Effect(EffectCondition.ON_USE, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 1, status=StatusType.DAMAGE_UP)], []),
                                   Skill("Upheaval", 2, 4, 6, 2, [], [[Effect(EffectCondition.ON_HEAD, EffectDetails.RAISE_NEXT_COIN, 2)]])]),  # TODO: Bust Tremor
    "LCB_Sinner_Gregor": Sinner("LCB Sinner Gregor", 146, 3, 7, 33, 33, [-25, 0, 50],
                                  [Skill("Swipe", 0, 3, 7, 1, [], [[Effect(EffectCondition.ON_HEAD, EffectDetails.APPLY_STATUS, 4, status=StatusType.RUPTURE)]]),
                                   Skill("Jag", 1, 4, 10, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.RAISE_STATUS_COUNT, 1, status=StatusType.RUPTURE),
                                                                   Effect(EffectCondition.ON_HEAD, EffectDetails.APPLY_STATUS, 1, status=StatusType.PIERCE_FRAGILITY)]]),
                                   Skill("Chop Up", 1, 5, 4, 2, [], [[Effect(EffectCondition.TARGET_HAS_STATUS_OF_AMOUNT, EffectDetails.COIN_HIT_MULT, 10, conditional_status=StatusType.RUPTURE, conditional_amount=1)],
                                                                     [Effect(EffectCondition.TARGET_HAS_STATUS_OF_AMOUNT, EffectDetails.COIN_HIT_MULT, 10, conditional_status=StatusType.RUPTURE, conditional_amount=1),
                                                                      Effect(EffectCondition.ON_HEAD, EffectDetails.HEAL_FOR_DAMAGE, 30)]])]),
    "LCB_Sinner_Faust": Sinner("LCB Sinner Faust", 171, 2, 4, 35, 28, [50, -25, 0],
                                 [Skill("Downward Slash", 2, 3, 7, 1, [], [[Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS, 1, status=StatusType.PARALYSIS)]]),  # TODO: Implement Paralysis
                                  Skill("Upward Slash", 2, 4, 4, 2, [], [[], [Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS_NEXT_TURN, 2, status=StatusType.OFFENSE_LEVEL_DOWN)]]),
                                  Skill("Drilling Stab", 1, 6, 2, 2, [], [[Effect(EffectCondition.ON_HEAD, EffectDetails.APPLY_STATUS_NEXT_TURN, 1, status=StatusType.ATTACK_POWER_DOWN)],
                                                                          [Effect(EffectCondition.ON_HIT, EffectDetails.APPLY_STATUS_NEXT_TURN, 1, status=StatusType.ATTACK_POWER_DOWN)]])]),
    "LCB_Sinner_Don_Quixote": Sinner("LCB Sinner Don Quixote", 134, 3, 6, 27, 36, [0, -25, 50],
                                 [Skill("Joust", 1, 3, 7, 1, [Effect(EffectCondition.ClASH_WIN, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 2, status=StatusType.HASTE)], []),
                                  Skill("Galloping Tilt", 1, 4, 10, 1, [Effect(EffectCondition.ClASH_WIN, EffectDetails.APPLY_STATUS_NEXT_TURN_ON_SELF, 2, status=StatusType.ATTACK_POWER)], []),
                                  Skill("For Justice!", 1, 3, 3, 3, [], [])]), # TODO: Implement Coin Power on Speed
}

if __name__ == '__main__':
    #combat([sinners["LCB_Sinner_Don_Quixote"], sinners["LCB_Sinner_Meursault"]])

    combatant_list = list(sinners.keys())

    num_of_combatants = len(combatant_list)
    win_stats = [0] * num_of_combatants
    num_of_fights = 0
    match_ups = []
    fights = []

    for i in range(len(combatant_list)):
        for j in range(i+1, len(combatant_list)):
            match_ups.append([combatant_list[i], combatant_list[j]])

    random.shuffle(match_ups)

    for match_up in match_ups:
        wins = [0, 0]
        num_of_fights += 1

        while wins[0] < FIRST_TO_X_WINS and wins[1] < FIRST_TO_X_WINS:
            fight_winner = combat([sinners[match_up[0]], sinners[match_up[1]]])

            wins[fight_winner] += 1

        if wins[0] == FIRST_TO_X_WINS:
            win_stats[combatant_list.index(match_up[0])] += 1
            fights.append(f"{sinners[match_up[0]].name} beasts {sinners[match_up[1]].name}")
        else:
            win_stats[combatant_list.index(match_up[1])] += 1
            fights.append(f"{sinners[match_up[1]].name} beasts {sinners[match_up[0]].name}")

    final_list = sorted(zip(win_stats, combatant_list), reverse=True)

    print("\nFight Results:")
    for fight in fights:
        print(fight)

    print("\nTotal Stats:")
    num_of_indv_fights = (len(combatant_list)-1)
    for combatant_stats in final_list:
        print(f"{sinners[combatant_stats[1]].name}: {combatant_stats[0]}-{num_of_indv_fights - combatant_stats[0]}")