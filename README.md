# This...is...JEO.PY!

A CLI for scoring _Jeopardy!_ It aims to make scoring while watching easy for touch typists.

The only house rule baked into the program is that Daily Doubles are valued at twice the clue's original value to obviate pausing the show.

## Usage

Requires Python 3. On Windows you will also need `pip install pyreadline`.

```bash
$ chmod +x jeo.py
$ ./jeo.py
```

```
> # award $1000 to player a
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
> # enter double jeopardy round
> double
```

Type `help` at the prompt for a full list of commands.

## R&D

- allow score multiple players in single entry (for ties), e.g. `2 mk`
- save entries to file / replay from file
- confirm exit
- undo
- reset score
- play theme song
- final jeopardy mode
- config file
- different daily double options
