#!/usr/bin/env python3

import locale
import time
import readline
from enum import Enum

VALID_JEOPARDY_AMOUNTS = [2, 4, 6, 8, 10]
VALID_DOUBLE_JEOPARDY_AMOUNTS = [s * 2 for s in VALID_JEOPARDY_AMOUNTS]
NUM_PLAYERS = 2
HELP_FILE="help_info.txt"


class Round(Enum):
    JEO = 1
    DOUBLE_JEO = 2
    FINAL_JEO = 3


class InputError(Exception):
    pass


class Game:
    def __init__(self):
        self.round = Round.JEO
        self.players = []

    def init_scores(self):
        self.scores = {}
        self.history = []
        self.undo_stack = []
        for player in self.players:
            self.add_to_player_score(player, 0)

    def print_sum_score(self):
        for k, v in self.scores.items():
            print(
                "{:>69}: {:>3}".format(
                    k, locale.format_string("$%1.0f", sum(v), grouping=True)
                )
            )

    def add_to_player_score(self, player, amount):
        self.scores.setdefault(player, []).append(amount)

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
            entry_to_undo = self.undo_stack[-1]
        except IndexError:
            return
        self.score_entry(entry_to_undo, undoing=True)
        self.undo_stack = self.undo_stack[:-1]

    def score_entry(self, entry, undoing=False):
        # get numeric val from entry
        # via https://stackoverflow.com/a/26825833
        raw_val = int("".join(filter(str.isdigit, entry)))

        if not undoing and not self.is_amount_valid(raw_val):
            print(
                "\aThat amount is invalid.\nValid amounts are: {}\nTry again.".format(
                    VALID_DOUBLE_JEOPARDY_AMOUNTS
                    if self.is_double_jeopardy()
                    else VALID_JEOPARDY_AMOUNTS
                )
            )
            return

        val = raw_val * 100

        players = []
        for p in self.players:
            if p in entry:
                players.append(p)

        if len(players) == 0:
            return

        is_wrong = "-" in entry
        is_daily_double = "*" in entry

        if is_wrong:
            val *= -1

        if is_daily_double:
            val *= 2

        if undoing:
            val *= -1

        for player in players:
            self.add_to_player_score(player, val)

        if undoing:
            entry_to_record = entry + " # undone"
        else:
            # don't push onto the undo stack if we're presently undoing,
            # otherwise a subsequent undo would redo
            self.undo_stack.append(entry)
            entry_to_record = entry

        self.history.append(entry_to_record)

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
