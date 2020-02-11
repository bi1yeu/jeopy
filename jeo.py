#!/usr/bin/env python3

import locale
import time
import readline
from enum import Enum

VALID_JEOPARDY_AMOUNTS = [2, 4, 6, 8, 10]
VALID_DOUBLE_JEOPARDY_AMOUNTS = [s * 2 for s in VALID_JEOPARDY_AMOUNTS]
NUM_PLAYERS = 2
HELP_FILE="help_info.txt"

class DailyDoubleRule(Enum):
    ORIGINAL_CLUE = 1
    DOUBLE_CLUE = 2
    TRUE_DD = 3 # stake double player's score

class Round(Enum):
    JEO = 1
    DOUBLE_JEO = 2
    FINAL_JEO = 3


class InputError(Exception):
    pass


class Game:
    def __init__(self):
        self.round = Round.JEO
        # self.dd_rule = DailyDoubleRule.DOUBLE_CLUE
        self.dd_rule = DailyDoubleRule.TRUE_DD
        self.players = []

    def init_scores(self):
        self.scores = []
        self.history = []
        self.undo_stack = []

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

    def setup_players(self):
        while len(self.players) < NUM_PLAYERS:
            try:
                player_full = input(
                    "Name of player {}: ".format(len(self.players) + 1)
                ).lower()
                player = player_full[0]
                idx = 1
                while player in self.players:
                    if idx >= len(player_full):
                        print("Let's try that again...")
                        raise InputError
                    player = player_full[idx]
                    idx += 1
                self.players += player
                print("We'll call them '{}'.".format(player))
            except InputError:
                continue
            except IndexError:
                continue

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
        self.setup_players()
        self.init_scores()

        print(
            "Instructions: Record a player's score for a clue with `<amount/100> <player>`\nE.g., to award $1,000 to player `{}`, enter:\n\n> 10 {}\n\nType `help` for more info.".format(
                self.players[0], self.players[0]
            )
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

    def reset(self):
        confirmation = input("Are you sure you want to reset scores to 0? [y/N]: ")
        if confirmation.strip().lower() == "y":
            self.init_scores()
            self.print_sum_score()

    def process_line(self, line):
        entry = line.lower().strip()
        try:
            if entry == "":
                return

            if entry[0] == "#":
                return

            if entry == "debug":
                import pdb; pdb.set_trace()

            if entry == "help":
                with open(HELP_FILE, "r") as f:
                    [print(line,end="") for line in f.readlines()]
                return

            if entry == "undo":
                self.undo()
                self.print_sum_score()
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
                self.reset()
                return

            self.score_entry(entry)
            self.print_sum_score()
        except ValueError:
            print("\aCouldn't understand input...please try again.")


if __name__ == "__main__":
    print("This...")
    print("       ...is...")
    print("               ...JEO.PY!")
    print(
        "--------------------------------------------------------------------------------"
    )

    locale.setlocale(locale.LC_ALL, "")

    game = Game()
    game.play()
