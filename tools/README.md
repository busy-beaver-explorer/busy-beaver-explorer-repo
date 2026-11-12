# Shared tools

Tools that are not about one machine. Each machine's folder in `../holdouts/` uses them as they are.

| path | what it is |
|---|---|
| `lean/TM/Basic.lean` | the semantics of any two-symbol machine in Lean: tapes, `step`, `steps`, `Halts`, and the shift-rule lemmas `cross_r`, `cross_l` |
| `lean/TM/Fin.lean` | a list simulator proved to agree with `steps`, so a bounded run from blank tape becomes a `decide +kernel` or `native_decide` goal (`blank_runs`) |
| `lean/TM/CTL.lean` | closed tape languages and their soundness (part of the library; not used by these two proofs) |
| `lean/Test/` | small tests of the library (BB(2), BB(4), a looping machine) |
| `lean/check.sh` | compiles the library, then a machine's files, with plain `lean` (no Lake); `.olean` files go to `out/` |
| `py/bbtools/machine.py` | the parser of the standard text format (`1RB0LE_...`) and a reference simulator |
| `py/bbtools/symtm.py` | symbolic simulation with runs `w^n` and unknown context, shift rules found on the spot, and Lean proofs written from the trace (`prove`, `rules_file`); the machines' `py/` scripts use it to write their Lean rule files |
| `py/bbtools/triage.py` | fits a growth exponent to each side of the tape from the output of `c/triage.c` and names its shape (the "sqrt/sqrt" on the status pages) |
| `c/tm.h`, `c/triage.c` | a fast direct simulator; `triage MACHINE STEPS` runs a machine from blank tape and prints its reach on each side at every power of two of steps, as one JSON line (`../holdouts/triage.json` holds its output for the two machines) |
| `pages/build_explainer.py` | a machine's interactive explainer page from its `status.json`: the table, where a halt can come from, the machine running in the browser, a space-time diagram, the records, the ledger of results, and the hand-written sections (the proof walkthrough) |
| `pages/build_status.py` | a machine's proof-status page from its `status.json`, every claim tagged by what it rests on: kernel, native, trusted, heuristic or open |

`../holdouts/build_pages.py` calls the two page builders for every machine.
