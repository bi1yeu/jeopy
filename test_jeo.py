import jeo


def test_jeo(mocker):
    entries = [
        "6* a-",
        "8* a",
        "help",
        "a2",
        "b2",
        "a4",
        "b4",
        "undo",
        "a8",
        "8ab",
        "6ab-",
        "10 b",
        "# comment ignored",
        "- 2 b",
        "6ab*",
        "10 ab",
        "double",
        "4 a-",
        "4 a-",
        "undo",
        "8ab*-",
        "16* b-",
        "16* a",
        "12 b",
        "2 b",
        "4 b",
        "4 a",
    ]

    mocker.patch("builtins.input", side_effect=entries)
    game = jeo.Game()
    game.players = ["a", "b"]
    game.dd_rule = jeo.DailyDoubleRule.TRUE_DD

    try:
        game.play()
    except StopIteration:
        pass
    assert game.scores == [
        {"a": -1000},
        {"a": 1000},
        {"a": 200},
        {"b": 200},
        {"a": 400},
        {"a": 800},
        {"a": 800, "b": 800},
        {"a": -600, "b": -600},
        {"b": 1000},
        {"b": -200},
        {"a": 1600, "b": 1200},
        {"a": 1000, "b": 1000},
        {"a": -400},
        {"a": -3800, "b": -3400},
        {"b": -2000},
        {"a": 2000},
        {"b": 1200},
        {"b": 400},
        {"a": 400},
    ]
    assert game.player_current_score("a") == 2400
    assert game.player_current_score("b") == -400
