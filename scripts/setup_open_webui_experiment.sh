#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$PWD/.experiment-workspace}"
TARGET="$ROOT/open-webui"
RESULTS="$ROOT/results"
REPO_URL="https://github.com/open-webui/open-webui.git"
PIN="0a7c15832fb30b1903753e83f81dc7d27e5b0944"

command -v git >/dev/null || { echo 'git is required' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'python3 is required' >&2; exit 1; }

mkdir -p "$ROOT" "$RESULTS"
if [ ! -d "$TARGET/.git" ]; then
  git clone --filter=blob:none --no-checkout "$REPO_URL" "$TARGET"
fi

git -C "$TARGET" fetch --depth=1 origin "$PIN"
git -C "$TARGET" checkout --detach "$PIN"
ACTUAL="$(git -C "$TARGET" rev-parse HEAD)"
[ "$ACTUAL" = "$PIN" ] || { echo "pin mismatch: $ACTUAL" >&2; exit 1; }

for strategy in plain structured decomposion; do
  for prompt in $(seq -w 1 10); do
    for run in 1 2 3; do
      mkdir -p "$RESULTS/$strategy/P$prompt/run-$run"
    done
  done
done

cat > "$ROOT/ENVIRONMENT.txt" <<EOF
experiment=open-webui-change-impact-v1
target_repo=$REPO_URL
target_commit=$PIN
created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python=$(python3 --version 2>&1)
git=$(git --version)
EOF

cat <<EOF
Ready.
Target:  $TARGET
Results: $RESULTS
Pinned:  $PIN

Run your coding agent from the target directory, one fresh session per prompt/strategy/run.
See experiments/open-webui/RUNBOOK.md in the decomposion repository.
EOF
