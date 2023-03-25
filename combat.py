import math
import random

import configs
from combant_info import CombatStats, Team
from effects import EffectTrigger, EffectDetails
from statuses import Status, StatusType
from tools import format_sources


def combat(fighting_sinners):

    combatants = [CombatStats(fighting_sinners[0]),
                  CombatStats(fighting_sinners[1])]

    team0 = Team()
    team1 = Team()

    team0.add_to_team(combatants[0])
    team1.add_to_team(combatants[1])

    if configs.COMBAT_VERBOSE:
        print(combatants[0].sinner.name + " vs " + combatants[1].sinner.name + "\n")

    while combatants[0].hp > 0 and combatants[1].hp > 0:
        i = 0
        for combatant in combatants:
            combatant.speed_roll()
            combatant.choose_skills([combatants[(i+1)%2]])
            i += 1

        if combatants[0].stagger_level > 0:
            if configs.COMBAT_VERBOSE:
                print(f"{combatants[1].sinner.name} strikes ones sided with {combatants[1].chosen_skill[0].skill.name}")
            combatants[1].chosen_skill[0].strike()
        elif combatants[1].stagger_level > 0:
            if configs.COMBAT_VERBOSE:
                print(f"{combatants[0].sinner.name} strikes ones sided with {combatants[0].chosen_skill[0].skill.name}")
            combatants[0].chosen_skill[0].strike()
        else:
            clash(combatants[0], 0, combatants[1], 0)

        if configs.COMBAT_VERBOSE:
            print("")

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


def clash(combatant1, skill1, combatant2, skill2):
    combatants_info = [combatant1, combatant2]
    skills = [combatant1.chosen_skill[skill1], combatant2.chosen_skill[skill2]]

    if configs.COMBAT_VERBOSE:
        print(f"{combatant1.sinner.name} (speed {combatant1.speed}) using {skills[0]} ({skills[0].skill.base} +{skills[0].skill.coin_bonus}) vs "
              f"{combatant2.sinner.name} (speed {combatant2.speed}) using {skills[1]} ({skills[1].skill.base} +{skills[1].skill.coin_bonus})")

    clashes = 0

    for skill in skills:
        skill.trigger_effect(EffectTrigger.ON_USE)

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
            skills[1].coins -= 1
        if clash_result[0][0] < clash_result[1][0]:
            skills[0].coins -= 1

    if combatants_info[0].hp > 0 and combatants_info[1].hp > 0:
        if skills[0].coins > 0:
            attacker = 0
            defender = 1
            if configs.COMBAT_VERBOSE:
                print(combatants_info[0].sinner.name + " wins clash")
        else:
            attacker = 1
            defender = 0
            if configs.COMBAT_VERBOSE:
                print(combatants_info[1].sinner.name + " wins clash")

        skills[attacker].trigger_effect(EffectTrigger.ClASH_WIN)
        skills[attacker].strike(clashes)



