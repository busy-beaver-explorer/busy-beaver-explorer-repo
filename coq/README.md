# busycoq proofs: two BB(6) holdouts never halt

These are Coq proofs that two six-state machines never halt from a blank tape. They are built on
[busycoq](https://github.com/meithecatte/busycoq), the Coq library of Turing machine semantics used for the bbchallenge
proofs:

| machine | bbchallenge id | final theorem | check time |
|---|---|---|---|
| `1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC` | 36670 | `nonhalt : ~ halts tm c0` in `H36670/H36670.v` | about 80 s |
| `1RB0LE_1RC---_1RD1RE_1LA0RF_0RC0LA_0LC0RB` | 113677 | `nonhalt : ~ halts tm c0` in `H113677/H113677.v` | about 3 min |

Both theorems use busycoq's own definitions, unchanged: `TM`, `step`, `halts` and `c0` (the blank tape in state A)
from `TM.v`, with 6 states and 2 symbols. For each of them, `Print Assumptions nonhalt` prints *Closed under the
global context*, so no axioms are used at all.

Both machines also have Lean proofs, in `../holdouts/M/lean/`. The Coq proofs use the same certificates (the Lean
tables, forms, rules and inequalities, read by the generators in `gen/`), but their own checker, written and proved
sound separately.

## Check

```sh
sh coq/build.sh                # clones busycoq at a fixed commit into coq/.busycoq, then compiles everything
sh coq/build.sh ../busycoq     # or use a busycoq checkout you already have
```

This needs Coq 8.18 (tested with 8.18.0; on Ubuntu 24.04, `sudo apt-get install coq`). The script copies the `.v`
files of this folder into busycoq's `verify/` folder and compiles them there in dependency order: busycoq's core
files `LibTactics`, `Helper`, `Pigeonhole`, `TM`, `Compute`, `Flip`, `Permute`, `Individual`, then `lib/`, then the
two proofs. It stops at the first file that fails, and prints the `Print Assumptions` result of each proof.
[`build.log`](build.log) is the output of a clean run.

## How the proofs work

Both proofs follow the shape of their Lean counterparts. A set `Good` of configurations contains a configuration
reached from blank tape, and from every `Good` configuration the machine makes at least one step to another `Good`
one. busycoq's `progress_nonhalt` turns that into `~ halts tm c0`. All the work is in proving the steps between
configurations whose counts are variables. That is done by a symbolic runner, proved sound once:

- [`lib/SymRun.v`](lib/SymRun.v) is the runner. A configuration is a list of tokens, and a token is either a single
  cell or a run `w^n` whose count `n` is linear in some variables. `auto` searches for a run from one configuration
  to a target. It takes single steps, crosses whole runs by shift rules it finds on the spot, and regroups runs
  (rotating `x (y x)^n = (x y)^n x`, splitting `w^(mq+r)` into `(w^m)^q w^r`, absorbing copies). `auto_sound` proves
  that an answer of `true` means the real machine goes from one to the other in at least one step, for every value
  of the variables. Targets are compared after a normal form (`norm01`, `normG`, `normL`, `normS`), each proved to
  keep the tape.
- [`lib/SymForms.v`](lib/SymForms.v) turns a symbolic run into a statement about the machine. It covers phase forms
  as templates, rules between forms at linear arguments (`rules_sound`), and equal forms (`formeq_sound`).
- [`lib/BB62.v`](lib/BB62.v) and [`lib/Individual62.v`](lib/Individual62.v) are busycoq's `BB52.v` and
  `Individual52.v` with a sixth state `F`.

Every run is evaluated by `vm_compute`. That is the bytecode evaluator Coq's kernel uses for its own conversion
checks, so it is part of what the kernel checks, like Lean's `decide`. It is not like `native_decide`: nothing is
compiled to machine code, and no axiom is added. Nothing here uses `native_compute`.

### 36670

[`H36670/H36670.v`](H36670/H36670.v) holds the certificate of the Lean proof (`lean/Tables.lean`):

- 62 phase templates, each with a round trip (`rounds_ok`) and an end of epoch (`ends_ok`);
- the start from blank tape (`start_ok`);
- the potential `j + 2k + pot t >= 215` (`tables_ok`).

The Lean proof needs `native_decide` for the start and the 62 ends (about 2.6 million symbolic moves). Here the
kernel checks them, in about a minute.

### 113677

- [`H113677/H113677_Rules.v`](H113677/H113677_Rules.v) has the 15 phase forms and the 27 rules of `py/macro.py`, each
  checked by the runner. It also has 7 identities between forms and the 7 cycles' k-fold repeats, by induction on k.
- [`H113677/H113677_Table.v`](H113677/H113677_Table.v) is the run from blank tape. The first 29,301 steps reach
  `O 14 37 11`, checked by the runner. The branch table then takes 196 moves to the last macro state before step
  10^30, `T2 34158019330534 128092572489511 160237983842729 41908435347077`. Numbers of 5000 or more are written
  `N.to_nat n%N`, so they are only compared by `lia` and never built in unary.
- [`H113677/H113677.v`](H113677/H113677.v) has the invariant `Good` (the inequalities of `lean/Closed.lean`), the
  20 move lemmas `mv_*`, `good_step` and `nonhalt`.

## Generators

The proof files are generated. Do not edit them by hand. Edit the generator, rerun it, and run
`sh scripts/check_generated.sh` to see that everything is current.

- [`gen/gen_m1.py`](gen/gen_m1.py) writes `H36670/H36670.v` from the Lean tables.
- [`gen/gen_m2_files.py`](gen/gen_m2_files.py) (with [`gen/gen_m2.py`](gen/gen_m2.py)) writes the three `H113677`
  files from the machine's `py/` folder and `lean/Closed.lean`.
- [`gen/m2_derived.v`](gen/m2_derived.v) and [`gen/m2_closed.v`](gen/m2_closed.v) are hand-written Coq that the
  generator splices into `H113677_Rules.v` and `H113677.v`: the induction proofs of the cycle repeats, and the move
  lemmas with `good_step`.

## License

`lib/BB62.v` and `lib/Individual62.v` are adapted from busycoq, which is MIT-licensed:
Copyright (c) 2023 Maja Kądziołka. busycoq itself is not copied into this repository; `build.sh` fetches it.
