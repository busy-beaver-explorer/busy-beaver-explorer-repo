#!/bin/sh
# Check the busycoq proofs that the two holdouts never halt.
#
# usage: sh coq/build.sh [BUSYCOQ]
#
# BUSYCOQ is a checkout of https://github.com/meithecatte/busycoq. Without it, the script clones busycoq at the commit
# these proofs were checked against into coq/.busycoq (needs git and network once). It copies lib/, H36670/ and
# H113677/ into busycoq's verify/ folder and compiles there, in dependency order: first busycoq's own core files, then
# ours. Needs Coq 8.18 (tested with 8.18.0). It stops at the first file that fails and prints Coq's output for it;
# for each final theorem it prints the result of `Print Assumptions nonhalt`.
set -e
COMMIT=bd2e36f6aa204eb011742d2ca6c8741102b2e59e      # busycoq master of 2 March 2025
HERE=$(cd "$(dirname "$0")" && pwd)
BC=${1:-}
if [ -z "$BC" ]; then
  BC="$HERE/.busycoq"
  if [ ! -d "$BC/.git" ]; then
    git init -q "$BC"
    git -C "$BC" fetch -q --depth 1 https://github.com/meithecatte/busycoq "$COMMIT"
    git -C "$BC" checkout -q FETCH_HEAD
  fi
fi
if [ -d "$BC/verify" ]; then V="$BC/verify"; elif [ -d "$BC/src/verify" ]; then V="$BC/src/verify"; else
  echo "no verify/ folder in $BC" >&2; exit 1; fi
cp "$HERE"/lib/*.v "$HERE"/H36670/*.v "$HERE"/H113677/*.v "$V"/
cd "$V"
LOG=$(mktemp)
for f in LibTactics Helper Pigeonhole TM Compute Flip Permute Individual BB62 Individual62 SymRun SymForms \
         H36670 H113677_Rules H113677_Table H113677; do
  t0=$(date +%s)
  if ! coqc -Q . BusyCoq "$f.v" > "$LOG" 2>&1; then
    echo "FAILED: $f.v" >&2; cat "$LOG" >&2; rm -f "$LOG"; exit 1
  fi
  echo "ok  $f.v  ($(( $(date +%s) - t0 )) s)"
  grep -A1 "^Axioms:\|Closed under the global context" "$LOG" || true
done
rm -f "$LOG"
