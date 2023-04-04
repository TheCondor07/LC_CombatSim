# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import configs
from combat import combat
from operator import itemgetter

from sinners import sinners

if __name__ == '__main__':

    #combat([sinners["The One Who Grips Faust"]], [sinners["LCB Sinner Meursault"]])

    """wins = [0,0]
    for i in range(1000):
        fight_winner = combat([sinners["R Corp. 4th Pack Rabbit Heathcliff"]],
               [sinners["N Corp. Grosẞhammer Meursault"]])

        wins[fight_winner] += 1

    print(wins)"""

    if configs.DO_FULL_TESTING:
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

            while wins[0] < configs.FIRST_TO_X_WINS and wins[1] < configs.FIRST_TO_X_WINS:
                fight_winner = combat([sinners[match_up[0]]], [sinners[match_up[1]]])

                wins[fight_winner] += 1

            if wins[0] == configs.FIRST_TO_X_WINS:
                win_stats[combatant_list.index(match_up[0])] += 1
                fights.append([[sinners[match_up[0]].name, sinners[match_up[1]].name], f"{sinners[match_up[0]].name} beats {sinners[match_up[1]].name} ({configs.FIRST_TO_X_WINS}-{wins[1]})", [wins[0], wins[1]]])
            else:
                win_stats[combatant_list.index(match_up[1])] += 1
                fights.append([[sinners[match_up[0]].name, sinners[match_up[1]].name], f"{sinners[match_up[1]].name} beats {sinners[match_up[0]].name} ({configs.FIRST_TO_X_WINS}-{wins[0]})", [wins[0], wins[1]]])

        final_list = sorted(zip(win_stats, combatant_list), reverse=True)

        print("\nFight Results:")

        total_stats_str = "\nTotal Stats:"
        num_of_indv_fights = (len(combatant_list)-1)
        ordered_fights_list = list()
        for combatant_stats in final_list:
            total_stats_str += f"\n{sinners[combatant_stats[1]].name} ({combatant_stats[0]}-{num_of_indv_fights - combatant_stats[0]})"

            temp_list = list()
            for fight in fights:
                if fight[0][0] == sinners[combatant_stats[1]].name or fight[0][1] == sinners[combatant_stats[1]].name:
                    temp_list.append(fight)

            for fight in temp_list:
                fights.remove(fight)

            stats_str = f"{sinners[combatant_stats[1]].name}: "
            stats_str2 = f"Opponent: "
            stats_str += ("\t" * (len(final_list) - len(temp_list) + 1))
            stats_str2 += ("\t" * (len(final_list) - len(temp_list) + 1))

            for second_combatant in final_list:
                found_fight = False
                temp_fight = None

                for fight in temp_list:
                    if (fight[0][0] == sinners[second_combatant[1]].name or fight[0][1] == sinners[second_combatant[1]].name) and second_combatant != combatant_stats:
                        if fight[0][0] == sinners[combatant_stats[1]].name:
                            stats_str += f"{fight[2][0]}\t"
                            stats_str2 += f"{fight[2][1]}\t"
                        else:
                            stats_str += f"{fight[2][1]}\t"
                            stats_str2 += f"{fight[2][0]}\t"
                        temp_fight = fight
                        found_fight = True
                        break

                if found_fight:
                    temp_list.remove(temp_fight)
                    ordered_fights_list.append(temp_fight)

            print(stats_str)
            print(stats_str2)

        for fight in ordered_fights_list:
            print(fight[1])

        print(total_stats_str)