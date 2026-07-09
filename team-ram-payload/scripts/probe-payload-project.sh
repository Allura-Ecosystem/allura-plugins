#!/usr/bin/env bash
set -euo pipefail

find_project() {
  local depth="$1"
  shift
  find . -maxdepth "$depth" \
    \( -path './.git' -o -path './node_modules' -o -path './.next' -o -path './.worktrees' -o -path './.agents/skills' -o -path './.opencode/node_modules' -o -path './.opencode/skills' \) -prune \
    -o "$@"
}

echo "== workspace =="
pwd
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  git rev-parse --show-toplevel
  git status --short --branch
else
  echo "not a git repository"
fi

echo
echo "== package manager =="
if [ -f pnpm-lock.yaml ]; then
  echo "pnpm"
elif [ -f yarn.lock ]; then
  echo "yarn"
elif [ -f package-lock.json ]; then
  echo "npm"
else
  echo "unknown"
fi

echo
echo "== scripts =="
if [ -f package.json ]; then
  node -e "const p=require('./package.json'); for (const [k,v] of Object.entries(p.scripts || {})) console.log(k + ': ' + v)"
else
  echo "package.json not found"
fi

echo
echo "== payload config candidates =="
find_project 4 -type f \( -name 'payload.config.ts' -o -name 'payload.config.js' -o -name 'payload.config.mjs' -o -name 'payload.config.cjs' \) -print | sort

echo
echo "== app route candidates =="
find_project 4 -type d \( -path './src/app' -o -path './app' -o -path './pages' \) -print | sort

echo
echo "== docs and agent guidance =="
find_project 4 -type f \( -name 'AGENTS.md' -o -name 'README.md' -o -name 'PROJECT.yaml' -o -name 'BLUEPRINT.md' -o -name 'SOLUTION-ARCHITECTURE.md' -o -name 'DATA-DICTIONARY.md' -o -name 'REQUIREMENTS-MATRIX.md' -o -name 'RISKS-AND-DECISIONS.md' -o -name 'IMPLEMENTATION-SOURCE-OF-TRUTH.md' \) -print | sort
