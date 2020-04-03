# This...is...JEO.PY!

A CLI for scoring _Jeopardy!_ It aims to make scoring while watching easy for touch typists.

## Usage

Requires Python >= 3.6. On Windows you will also need `pip install pyreadline`.

```bash
$ chmod +x jeo.py
$ ./jeo.py
```

```
> # award $1,000 to player a
> 10 a
                                                                    a: $1,000
                                                                    z:  $0
> # deduct $600 from player z
> 6 z-
                                                                    a: $1,000
                                                                    z: $-600
> # award daily double to a (original score is doubled)
> 2* a
                                                                    a: $1,400
                                                                    z: $-600
> # spacing and order doesn't matter
> -z6
                                                                    a: $1,400
                                                                    z: $-1,200
> # score two players simultaneously (as in a tie)
> 2 az
                                                                    a: $1,600
                                                                    z: $-1,000
> # enter double jeopardy round
> double
>>
```

Type `help` at the prompt for a full list of commands.

## Development

To run tests:

```
pip install pytest pytest-mock
pytest
```

Type checking:

```
pip install mypy
mypy jeo.py
```

## R&D

- [x] allow score multiple players in single entry (for ties), e.g. `2 mk`
- [x] undo
- [ ] save entries to file / replay from file
- [x] config file
- [x] different daily double options, e.g. true dd
- [ ] per-player daily double options
- [ ] tutorial mode
- [ ] better commenting support
- [ ] confirm exit
- [x] reset score
- [ ] play theme song lol
- [ ] final jeopardy mode
- [x] type hints
- [ ] single player mode
- [ ] summary statistics
