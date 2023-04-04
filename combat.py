import math
import random

import configs
from combant_info import CombatStats, Team
from effects import EffectTrigger, EffectDetails
from statuses import Status, StatusType
from tools import format_sources


def combat(fighters_team_1: list, fighters_team_2: list):
    teams = [Team(), Team()]

    teams[0].add_to_team(fighters_team_1)
    teams[1].add_to_team(fighters_team_2)
    teams[0].opponents = teams[1]
    teams[1].opponents = teams[0]

    if configs.COMBAT_VERBOSE:
        print(f"{teams[0]} vs {teams[1]}\n")

    second_skill_slot = 0
    third_skill_slot = 0

    turn = 0
    if configs.GAIN_SKILL_SLOTS:
        second_skill_slot = random.randrange(2, 6)
        third_skill_slot = random.randrange(7, 11)

    while len(teams[0].get_alive_sinners()) > 0 and len(teams[1].get_alive_sinners()) > 0:
        turn += 1
        if configs.GAIN_SKILL_SLOTS:
            if turn == second_skill_slot or turn == third_skill_slot:
                if configs.COMBAT_VERBOSE:
                    print("Gain Skill slots")
                teams[0].add_skill_slot()
                teams[1].add_skill_slot()

        if configs.COMBAT_VERBOSE:
            print(f"Turn {turn}")
        combatants = teams[0].get_alive_sinners() + teams[1].get_alive_sinners()
        random.shuffle(combatants)

        for combatant in combatants:
            combatant.speed_roll()
        combatants.sort(key=lambda x: x.speed, reverse=True)

        teams[0].turn_order = []
        teams[1].turn_order = []
        for combatant in combatants:
            if combatant.team == teams[0]:
                teams[0].turn_order.append(combatant)
            else:
                teams[1].turn_order.append(combatant)

        teams[0].choose_skills()
        teams[1].choose_skills()

        for combatant in combatants:
            for skill in combatant.skill_slots:
                if combatant.can_act() and not skill.has_been_used and skill.opponent.hp > 0:
                    skill.has_been_used = True
                    skill.trigger_effect(EffectTrigger.ON_USE)

                    if skill.is_clashing():
                        skill.opponent.skill_slots[skill.targeted_slot].has_been_used = True
                        skill.opponent.skill_slots[skill.targeted_slot].trigger_effect(EffectTrigger.ON_USE)
                        clash(skill.combatant, skill.combatant.skill_slots.index(skill), skill.opponent, skill.targeted_slot)
                    else:
                        if configs.COMBAT_VERBOSE:
                            print(f"{skill.combatant.sinner.name} strikes one-sided against {skill.opponent.sinner.name} with {skill.skill.name}")
                            skill.strike()

                    if configs.COMBAT_VERBOSE:
                        print("")

        for combatant in combatants:
            combatant.end_of_turn()

    if len(teams[0].get_alive_sinners()) > 0:
        winner = 0
        loser = 1
    else:
        winner = 1
        loser = 0

    if configs.SHOW_BATTLE_RESULTS:
        print(f"{teams[winner]} beat {teams[loser]}")

    return winner


def clash(combatant1, skill1, combatant2, skill2):
    combatants_info = [combatant1, combatant2]
    skills = [combatant1.skill_slots[skill1], combatant2.skill_slots[skill2]]

    if configs.COMBAT_VERBOSE:
        print(f"{combatant1.sinner.name} (speed {combatant1.speed}) using {skills[0]} ({skills[0].skill.base} +{skills[0].skill.coin_bonus}) vs "
              f"{combatant2.sinner.name} (speed {combatant2.speed}) using {skills[1]} ({skills[1].skill.base} +{skills[1].skill.coin_bonus})")

    clashes = 0

    while skills[0].coins > 0 and skills[1].coins > 0:
        clashes += 1

        combat_str = ""

        if configs.COMBAT_VERBOSE:
            combat_str += f"Clash {clashes}:"

        clash_result = [[]]*2

        for combatant in range(2):
            opponent = (combatant+1) % 2
            clash_result[combatant] = skills[combatant].get_clash()

            if configs.COMBAT_VERBOSE:
                combat_str += f"[{skills[combatant].coins} coins] {clash_result[combatant][0]}"

                if configs.SHOW_BONUSES:
                    combat_str += f" ({format_sources(clash_result[combatant][1])})"

                if combatant == 0:
                    combat_str += " vs "

        if configs.COMBAT_VERBOSE:
            print(combat_str)

        if clash_result[0][0] > clash_result[1][0]:
            if(len(skills[1].coin_effects)) > 0:
                skills[1].coin_effects.pop(0)
            skills[1].coins -= 1
        if clash_result[0][0] < clash_result[1][0]:
            if (len(skills[0].coin_effects)) > 0:
                skills[0].coin_effects.pop(0)
            skills[0].coins -= 1

    if combatants_info[0].hp > 0 and combatants_info[1].hp > 0:
        if skills[0].coins > 0:
            attacker = 0
            defender = 1

        else:
            attacker = 1
            defender = 0

        if configs.GAIN_LOSE_SANITY:
            combatants_info[attacker].gain_lose_sp(round(10 * (1 + clashes * 0.25)))

        if configs.COMBAT_VERBOSE:
            print(combatants_info[attacker].sinner.name + " wins clash")

        skills[attacker].trigger_effect(EffectTrigger.ClASH_WIN)
        skills[defender].trigger_effect(EffectTrigger.ClASH_LOSE)
        skills[attacker].strike(clashes)



