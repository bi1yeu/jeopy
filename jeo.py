#!/usr/bin/env python3

import locale
import time
import readline
from enum import Enum

VALID_JEOPARDY_AMOUNTS = [2, 4, 6, 8, 10]
VALID_DOUBLE_JEOPARDY_AMOUNTS = [s * 2 for s in VALID_JEOPARDY_AMOUNTS]
NUM_PLAYERS = 2


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
        self.scores = {}
        self.history = []

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
                self.add_to_player_score(player, 0)
            except InputError:
                continue

    def is_double_jeopardy(self):
        return self.round == Round.DOUBLE_JEO

    def is_final_jeopardy(self):
        return self.round == Round.FINAL_JEO

    def play(self):
        self.setup_players()

        print(
            "Instructions: Record a player's score for a clue with `<amount / 100> <player>`\nE.g., to award $1,000 to player `{}`, enter:\n\n> 10 {}\n\nType `help` for more info.".format(
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

    def process_line(self, line):
        entry = line.lower().strip()

        try:
            if entry == "":
                return

            if entry[0] == "#":
                return

            if entry == "help":
                print(
                    "Available commands:"
                    + "\n<amount / 100> <player>[*][-]:\tadd amount to player's score. `*` denotes daily double (provided amount is doubled). `-` to subtract amount."
                    + "\nhelp:\t\t\t\tshow this info"
                    + "\nscores:\t\t\t\tshow the individual scores that were recorded for each player"
                    + "\nregular:\t\t\t\tenter regular Jeopardy round"
                    + "\ndouble:\t\t\t\tenter Double Jeopardy round"
                    + "\nfinal:\t\t\t\tenter Final Jeopardy round"
                )
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

            # get numeric val from entry
            # via https://stackoverflow.com/a/26825833
            raw_val = int("".join(filter(str.isdigit, entry)))

            if not self.is_amount_valid(raw_val):
                print(
                    "\aThat amount is invalid.\nValid amounts are: {}\nTry again.".format(
                        VALID_DOUBLE_JEOPARDY_AMOUNTS
                        if self.is_double_jeopardy()
                        else VALID_JEOPARDY_AMOUNTS
                    )
                )
                return

            val = raw_val * 100

            player = None
            for p in self.players:
                if p in entry:
                    player = p
                    break

            if player is None:
                return

            if not player in self.players:
                print(
                    "\aThat player is invald.\nValid players are: {}\nTry again.".format(
                        self.players
                    )
                )
                return

            is_wrong = "-" in entry
            is_daily_double = "*" in entry

            if is_wrong:
                val *= -1

            if is_daily_double:
                val *= 2

            if player[-1] == "*":
                player = player[0]
                val *= 2

            self.add_to_player_score(player, val)
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
