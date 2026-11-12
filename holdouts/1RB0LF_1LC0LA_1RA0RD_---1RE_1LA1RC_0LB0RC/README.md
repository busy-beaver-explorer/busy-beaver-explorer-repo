# 1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC

bbchallenge id 36670. It does **not halt** from blank tape, and this is proved twice:

- in Coq, `nonhalt : ~ halts tm c0` in [`../../coq/H36670/H36670.v`](../../coq/H36670/H36670.v), on top of busycoq,
  checked by Coq's kernel alone with no axioms (see [`../../coq/README.md`](../../coq/README.md));
- in Lean, `H36670.nonhalting` in `lean/Cert.lean` (the kernel for the rules and the 62 round trips, `native_decide`
  for the start and the 62 ends of an epoch).

Both use the same certificate, the tables of `lean/Tables.lean`. The pages
[`explainer.html`](../../pages/holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/explainer.html) (the machine
running in the browser and the proof step by step) and
[`proof-status.html`](../../pages/holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/proof-status.html) are built
from `status.json`.

| state | read 0 | read 1 |
|---|---|---|
| A | 1RB | 0LF |
| B | 1LC | 0LA |
| C | 1RA | 0RD |
| D | --- | 1RE |
| E | 1LA | 1RC |
| F | 0LB | 0RC |

## What it does

Each time B reaches the left end the tape reads `B> 00 (01)^a 000 (01)^b 000 …`, a list of counts written as
stretches of `01` separated by short words. The rightward sweep turns `010101` into `011001` (`sweep_right`, 14
steps a copy); the leftward sweep turns it back (`sweep_left`, 22 steps a copy).

- **Round trip**: a drops by 3.
- **Regimes**: the rest of the list runs through one of four periodic patterns, R0–R3, with periods 15, 22, 16
  and 9 round trips; per period b grows by 99, 141, 99 and 57 (always a multiple of 3, and a ≡ 1 mod 3 throughout).
- **Epochs**: when a is used up (a = 4), the left end is rebuilt and b (plus a constant) becomes the new a, after
  a transient of up to ~150 round trips the list is in one of the four regimes again. The first counts of the
  epochs along the run are 4, 12, 20, 38, 68, 122, 240, 484, 1002, 2104, 4375, … (a new epoch is seen at 649·10⁶
  steps).

The machine halts only when D reads a 0, i.e. after `C> 1 0`; C always sees `1 1` in the run.

## What is proved, and where

- `lean/Blank.lean` (generated): the halting configurations; no halt in 10⁴ steps (kernel) and 10⁷ (`native_decide`).
- `lean/Rules.lean` (kernel, written by `py/rules.py`): the two sweeps and the halting situations (`halt_C`,
  `halt_E`, `halt_F`, `halt_D`).
- `lean/SymCheck.lean` (kernel): a symbolic checker for configurations whose tape is a list of cells and runs
  `w^n` with n linear in some variables. `auto` finds the moves by itself (crossing a run with a shift rule found
  on the spot, else one machine step) and compares normal forms each time the head is at the left end;
  `auto_reach` proves that a successful run means the machine really goes from the one configuration to the other,
  for every value of the variables.
- `lean/Tables.lean` (written by `py/cert.py` from `py/cert_data.json`): the 62 phase templates
  `B> 00 (01)^(3k+4) 000 (01)^(3j+β) rest` of the four regimes (15 + 22 + 16 + 9), the successor of each phase and
  the increase of j per round trip, the phase and counts reached at the end of an epoch, and a potential `pot`.
- `lean/Cert.lean`: the proof.
  - `round_0` … `round_61` (kernel): template t at [k + 1, j] reaches template `nxt t` at [k, j + dj t]
    (200–2,500 symbolic moves each).
  - `ends_ok` (`native_decide`): template t at [0, j + 200] reaches template `endT t` at
    [j + endC1 t, endC2 t] (the end of an epoch, 4,200–127,000 symbolic moves each, 2.5 million in all).
  - `start_ok` (`native_decide`): blank tape reaches template 31 (R1, phase 16) at [38, 163], i.e. a = 118 and
    b = 496, at step 1,277,431 (148,000 symbolic moves).
  - `tables_ok` (kernel): j + 2k + pot t never decreases in a round and is at least 215 after an end, so j ≥ 200
    whenever k = 0 and an end case applies.
  - `nonhalting`: so the run from blank tape goes through these configurations forever; `#print axioms` lists only
    `propext`, `Quot.sound` and the two `native_decide` axioms.
- `py/regimes.py`, `py/endcases.py` (our code, using `c/simfrom.c`): how the regimes and end cases were found,
  by concrete simulation.
- `c/visits.c` (trusted, our code): in the first 2·10⁸ steps the machine is in state D 22,202,037 times, always on a 1.

`lean/check.sh` takes about 5 minutes on one core. The kernel runs out of memory (over 6 GB) on the start run, so
the start and the end cases are evaluated by compiled code. The numbers in `cert_data.json` need no trust: a wrong
one makes a check fail.

## The Coq proof

`coq/H36670/H36670.v` is generated from `lean/Tables.lean` by `coq/gen/gen_m1.py`. It states the 62 templates as
symbolic configurations of `coq/lib/SymRun.v`, a symbolic runner proved sound against busycoq's semantics, and
checks the 62 round trips (`rounds_ok`), the 62 ends of an epoch (`ends_ok`), the start (`start_ok`) and the tables
(`tables_ok`) by `vm_compute`, the evaluator inside Coq's kernel. `good_step` and `nonhalt` are the same induction as
in Lean. `Print Assumptions nonhalt` prints *Closed under the global context*. It checks in about 80 s, so the two
pieces that rest on `native_decide` in Lean are kernel-checked there.

## What is open, next steps

Nothing about halting. A Lean proof by the kernel alone would need the long runs cut into pieces of a few thousand
moves with the intermediate configurations written out (about 900 pieces, roughly 2 hours of kernel time); the Coq
proof already gives a kernel-only check.

## Check

```sh
sh coq/build.sh                       # the Coq proofs (both machines; fetches busycoq, needs Coq 8.18)
. /etc/profile.d/lean.sh && holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/lean/check.sh
python3 holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/py/rules.py     # rewrites lean/Rules.lean
python3 holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/py/cert.py      # rewrites lean/Tables.lean
python3 holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC/py/turns.py 1e6 | grep ' L  B> '   # the list at each left turn
```
