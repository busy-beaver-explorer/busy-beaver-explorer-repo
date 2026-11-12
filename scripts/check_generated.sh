#!/bin/sh
# Regenerate every generated file in the repository and fail if any of them differs from the committed version.
#
# usage: sh scripts/check_generated.sh        (from anywhere; needs python3 and git, takes about 15 s)
#
# What is generated, and from what:
#   holdouts/M/lean/*.lean      Lean files written by the machine's py/ scripts (see each holdouts/M/README.md)
#   holdouts/M/status.json      its "explainer.sections" (the proof walkthrough), by py/proof_page.py from
#                               py/proof_page.html
#   coq/H36670/, coq/H113677/   the Coq proofs, by coq/gen/gen_m1.py and coq/gen/gen_m2_files.py
#   pages/                      the site, by holdouts/build_pages.py from the status.json files
# So after editing a source, run this script, look at `git diff`, and commit the regenerated files with it.
set -e
cd "$(dirname "$0")/.."
M1=holdouts/1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC
M2=holdouts/1RB0LE_1RC---_1RD1RE_1LA0RF_0RC0LA_0LC0RB
run() { echo "== $*"; "$@" > /dev/null; }
run python3 $M1/py/cert.py
for s in route rules cycle phase branch ends table closed; do run python3 $M2/py/$s.py; done
run python3 $M1/py/proof_page.py
run python3 $M2/py/proof_page.py
run python3 coq/gen/gen_m1.py
run python3 coq/gen/gen_m2_files.py
run python3 holdouts/build_pages.py
if [ -n "$(git status --porcelain -- holdouts coq pages)" ]; then
  echo "These generated files differ from what is committed:" >&2
  git status --porcelain -- holdouts coq pages >&2
  git --no-pager diff --stat -- holdouts coq pages >&2
  exit 1
fi
echo "all generated files are current"
