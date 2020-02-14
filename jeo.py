#!/usr/bin/env python3

import json
import locale
import readline
import time
from enum import Enum

VALID_JEOPARDY_AMOUNTS = [2, 4, 6, 8, 10]
VALID_DOUBLE_JEOPARDY_AMOUNTS = [s * 2 for s in VALID_JEOPARDY_AMOUNTS]
HELP_FILE = "help_info.txt"
CONFIG_FILE = "config.json"


class DailyDoubleRule(Enum):
    ORIGINAL_CLUE = 1
    DOUBLE_CLUE = 2
    TRUE_DD = 3  # stake double player's score


DD_RULE_DESCS = {
    DailyDoubleRule.ORIGINAL_CLUE: "Clue face value",
    DailyDoubleRule.DOUBLE_CLUE: "Double clue face value",
    DailyDoubleRule.TRUE_DD: "True Daily Double",
}


class Round(Enum):
    JEO = 1
    DOUBLE_JEO = 2
    FINAL_JEO = 3


class InputError(Exception):
    pass


def solicit_player_names(num_players):
    players = []
    while len(players) < num_players:
        try:
            player_full = input("Name of player {}: ".format(len(players) + 1)).lower()
            player = player_full[0]
            idx = 1
            while player in players:
                if idx >= len(player_full):
                    print("Let's try that again...")
                    raise InputError
                player = player_full[idx]
                idx += 1
            players += player
            print("We'll call them '{}'.".format(player))
        except InputError:
            continue
        except IndexError:
            continue
    return players


def solicit_dd_rule():
    print("Choose Daily Double scoring strategy:")
    for k, v in DD_RULE_DESCS.items():
        print("{}. {}".format(k.value, v))
    dd_rule = None
    while dd_rule is None:
        try:
            raw_selection = input("Enter Daily Double scoring strategy: ")
            dd_rule = DailyDoubleRule(int(raw_selection))
        except ValueError:
            pass
    return dd_rule


class Game:
    def __init__(self):
        self.round = Round.JEO
        self.read_config()
        self.init_scores()

    def read_config(self):
        loaded_saved_config = False
        try:
            with open(CONFIG_FILE, "r") as config_file:
                self.config = json.load(config_file)
                loaded_saved_config = True
        except FileNotFoundError:
            print("Welcome to JEOPY!\n")
            self.solicit_settings(save_and_apply=True)

        self.dd_rule = DailyDoubleRule(self.config["dd_rule"])

        self.players = self.config.get("players", [])
        self.num_players = len(self.players) or self.config["num_players"]

        if loaded_saved_config:
            print("Loaded saved settings. Type `settings` to change configuration.")
            print("Players: " + ", ".join(self.players))
            print("Daily Double scoring strategy: " + DD_RULE_DESCS[self.dd_rule])

    def solicit_settings(self, save_and_apply=False):
        num_players = None
        while num_players is None:
            try:
                num_players = int(input("How many players? "))
            except ValueError:
                print("Please enter a number")

        players = solicit_player_names(num_players)
        dd_rule = solicit_dd_rule().value

        if not save_and_apply:
            confirm_save = input("Do you want to save these settings? [y/N]: ")
        if save_and_apply or confirm_save.strip().lower() == "y":
            with open(CONFIG_FILE, "w") as config_file:
                config = {
                    "num_players": len(players),
                    "players": players,
                    "dd_rule": dd_rule,
                }
                json.dump(config, config_file)
                if save_and_apply:
                    self.config = config
                    print("Settings saved for next time.")
            if not save_and_apply:
                print("Settings successfully saved. They will take effect next game.")
        else:
            print("Settings not saved.")

    def init_scores(self):
        self.scores = []
        self.history = []

    def player_current_score(self, target_player):
        total = 0
        for players_amounts in self.scores:
            for player, amount in players_amounts.items():
                if player == target_player:
                    total += amount
        return total

    def print_sum_score(self):
        summed_scores = {}

        for players_amounts in self.scores:
            for player, amount in players_amounts.items():
                if player not in summed_scores:
                    summed_scores[player] = 0
                summed_scores[player] += amount

        for player in self.players:
            player_total = summed_scores.get(player, 0)
            print(
                "{:>69}: {:>3}".format(
                    player, locale.format_string("$%1.0f", player_total, grouping=True)
                )
            )

    def add_to_players_scores(self, player_amounts):
        self.scores.append(player_amounts)

    def is_double_jeopardy(self):
        return self.round == Round.DOUBLE_JEO

    def is_final_jeopardy(self):
        return self.round == Round.FINAL_JEO

    def calculate_daily_double_amount(self, player, clue_amount):
        if self.dd_rule == DailyDoubleRule.ORIGINAL_CLUE:
            awarded_amount = clue_amount
        elif self.dd_rule == DailyDoubleRule.DOUBLE_CLUE:
            awarded_amount = clue_amount * 2
        elif self.dd_rule == DailyDoubleRule.TRUE_DD:
            # if a player has less than min_amount, they can still stake up to
            # min_amount
            min_amount = VALID_JEOPARDY_AMOUNTS[-1] * 100
            if self.is_double_jeopardy():
                min_amount = VALID_DOUBLE_JEOPARDY_AMOUNTS[-1] * 100
            player_score = self.player_current_score(player)
            awarded_amount = max(player_score, min_amount)
        return awarded_amount

    def play(self):
        print(
            "--------------------------------------------------------------------------------\n"
            + "Instructions: Record a player's score for a clue with `<amount/100> <player>`\nE.g., to award $1,000 to player {}, enter:\n\n> 10 {}\n\nType `help` for more info.\n".format(
                self.players[0], self.players[0]
            )
            + "--------------------------------------------------------------------------------\n"
        )

        while True:
            prompt = ">> " if self.is_double_jeopardy() else "> "
            self.process_line(input(prompt))

    def is_amount_valid(self, amount):
        return (
            not self.is_double_jeopardy() and abs(amount) in VALID_JEOPARDY_AMOUNTS
        ) or (
            self.is_double_jeopardy() and abs(amount) in VALID_DOUBLE_JEOPARDY_AMOUNTS
        )

    def undo(self):
        try:
            self.scores = self.scores[:-1]
            self.history = self.history[:-1]
        except IndexError:
            return

    def score_entry(self, entry):
        # get numeric amount from entry
        # via https://stackoverflow.com/a/26825833
        raw_amount = int("".join(filter(str.isdigit, entry)))

        if not self.is_amount_valid(raw_amount):
            print(
                "\aThat amount is invalid.\nValid amounts are: {}\nTry again.".format(
                    VALID_DOUBLE_JEOPARDY_AMOUNTS
                    if self.is_double_jeopardy()
                    else VALID_JEOPARDY_AMOUNTS
                )
            )
            return

        is_wrong = "-" in entry
        is_daily_double = "*" in entry

        players_amounts = {}

        # even in the case of "ties", we need to score each player
        # individiually since a true daily double may result in different point
        # amounts being awarded.
        for player in self.players:
            if player in entry:
                amount = raw_amount * 100

                if is_daily_double:
                    amount = self.calculate_daily_double_amount(player, amount)

                if is_wrong:
                    amount *= -1

                players_amounts[player] = amount

        if len(players_amounts) > 0:
            self.add_to_players_scores(players_amounts)
            self.history.append(entry)
        else:
            print("\aUnknown player. Try again.")

    def confirm_reset(self):
        confirmation = input("Are you sure you want to reset scores to 0? [y/N]: ")
        if confirmation.strip().lower() == "y":
            self.init_scores()
            self.print_sum_score()
            return True
        return False

    def process_line(self, line):
        entry = line.lower().strip()
        try:
            if entry == "":
                return

            if entry[0] == "#":
                return

            if entry == "debug":
                import pdb

                pdb.set_trace()

            if entry == "help":
                with open(HELP_FILE, "r") as f:
                    [print(line, end="") for line in f.readlines()]
                return

            if entry == "undo":
                self.undo()
                self.print_sum_score()
                return

            if entry == "settings":
                self.solicit_settings()
                return

            if entry == "scores":
                print(self.scores)
                return

            if entry == "history":
                [print(h) for h in self.history]
                return

            if entry == "regular":
                self.round = Round.JEO
                return

            if entry == "double":
                self.round = Round.DOUBLE_JEO
                return

            if entry == "final":
                # self.round = Round.FINAL_JEO
                print("Sorry, that isn't implemented yet.")
                return

            if entry == "reset":
                self.confirm_reset()
                return

            self.score_entry(entry)
            self.print_sum_score()
        except ValueError:
            print("\aCouldn't understand input...please try again.")


if __name__ == "__main__":
    print(
        """
================================================================================
    _____  ________   ______      _______   __      __  __
   /     |/        | /      \    /       \ /  \    /  |/  |
   $$$$$ |$$$$$$$$/ /$$$$$$  |   $$$$$$$  |$$  \  /$$/ $$ |
      $$ |$$ |__    $$ |  $$ |   $$ |__$$ | $$  \/$$/  $$ |
 __   $$ |$$    |   $$ |  $$ |   $$    $$/   $$  $$/   $$ |
/  |  $$ |$$$$$/    $$ |  $$ |   $$$$$$$/     $$$$/    $$/
$$ \__$$ |$$ |_____ $$ \__$$ |__ $$ |          $$ |     __
$$    $$/ $$       |$$    $$//  |$$ |          $$ |    /  |
 $$$$$$/  $$$$$$$$/  $$$$$$/ $$/ $$/           $$/     $$/
================================================================================
"""
    )
    locale.setlocale(locale.LC_ALL, "")

    game = Game()
    game.play()
