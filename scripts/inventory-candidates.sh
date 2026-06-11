#!/usr/bin/env bash
set -euo pipefail

output="${1:?usage: inventory-candidates.sh <output-json>}"
temp_file="$(mktemp)"
trap 'rm -f "${temp_file}"' EXIT

hash_tree() {
  local path="$1"

  find "${path}" -type f -print0 \
    | sort -z \
    | xargs -0 -r sha256sum \
    | sha256sum \
    | awk '{print $1}'
}

find "${HOME}/.claude/plugins" "${HOME}/plugins" \
  -type f \
  \( -path '*/.claude-plugin/plugin.json' \
    -o -path '*/.codex-plugin/plugin.json' \) \
  -print 2>/dev/null \
  | while IFS= read -r manifest; do
      dirname "$(dirname "${manifest}")"
    done \
  | sort -u \
  | while IFS= read -r package_root; do
      claude_manifest="${package_root}/.claude-plugin/plugin.json"
      codex_manifest="${package_root}/.codex-plugin/plugin.json"
      primary_manifest="${claude_manifest}"

      if [[ ! -f "${primary_manifest}" ]]; then
        primary_manifest="${codex_manifest}"
      fi

      name="$(jq -r '.name // empty' "${primary_manifest}")"
      version="$(jq -r '.version // "unknown"' "${primary_manifest}")"

      if [[ -z "${name}" ]]; then
        continue
      fi

      jq -cn \
        --arg name "${name}" \
        --arg version "${version}" \
        --arg path "${package_root}" \
        --arg tree_hash "$(hash_tree "${package_root}")" \
        --argjson claude "$([[ -f "${claude_manifest}" ]] && printf true || printf false)" \
        --argjson codex "$([[ -f "${codex_manifest}" ]] && printf true || printf false)" \
        '{
          name: $name,
          version: $version,
          path: $path,
          manifests: {
            claude: $claude,
            codex: $codex
          },
          tree_sha256: $tree_hash
        }' >>"${temp_file}"
    done

jq -s 'sort_by(.name, .path)' "${temp_file}" >"${output}"
