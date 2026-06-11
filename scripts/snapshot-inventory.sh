#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
run_dir="${repo_root}/evidence/inventory/${timestamp}"
raw_dir="${run_dir}/raw"
backup_dir="${repo_root}/evidence/backups/${timestamp}"

mkdir -p "${raw_dir}" "${backup_dir}"

copy_if_present() {
  local source="$1"
  local target="$2"

  if [[ -f "${source}" ]]; then
    cp --preserve=mode,timestamps "${source}" "${target}"
  fi
}

archive_if_present() {
  local source="$1"
  local target="$2"

  if [[ -d "${source}" ]]; then
    tar -C "$(dirname "${source}")" -czf "${target}" "$(basename "${source}")"
  fi
}

hash_tree() {
  local path="$1"

  if [[ ! -d "${path}" ]]; then
    printf '%s' "missing"
    return
  fi

  find "${path}" -type f -print0 \
    | sort -z \
    | xargs -0 -r sha256sum \
    | sha256sum \
    | awk '{print $1}'
}

copy_if_present "${HOME}/.claude/settings.json" "${backup_dir}/claude-settings.json"
copy_if_present \
  "${HOME}/.claude/plugins/installed_plugins.json" \
  "${backup_dir}/claude-installed-plugins.json"
copy_if_present "${HOME}/.codex/config.toml" "${backup_dir}/codex-config.toml"
copy_if_present \
  "${HOME}/.agents/plugins/marketplace.json" \
  "${backup_dir}/codex-marketplace.json"

archive_if_present \
  "${HOME}/.claude/plugins/marketplaces" \
  "${backup_dir}/claude-marketplaces.tar.gz"
archive_if_present "${HOME}/plugins" "${backup_dir}/codex-local-plugins.tar.gz"

claude plugin list --available --json >"${raw_dir}/claude-plugin-list.json"
codex plugin list --available --json >"${raw_dir}/codex-plugin-list.json"

find "${HOME}/.claude/plugins" "${HOME}/plugins" \
  -type f \
  \( -path '*/.claude-plugin/plugin.json' \
    -o -path '*/.codex-plugin/plugin.json' \
    -o -path '*/.claude-plugin/marketplace.json' \
    -o -path '*/.agents/plugins/marketplace.json' \) \
  -print 2>/dev/null \
  | sort >"${raw_dir}/manifest-paths.txt"

jq -n \
  --arg generated_at "${timestamp}" \
  --arg claude_marketplaces_hash "$(hash_tree "${HOME}/.claude/plugins/marketplaces")" \
  --arg codex_plugins_hash "$(hash_tree "${HOME}/plugins")" \
  --arg claude_settings_hash "$(
    [[ -f "${HOME}/.claude/settings.json" ]] \
      && sha256sum "${HOME}/.claude/settings.json" | awk '{print $1}' \
      || printf '%s' "missing"
  )" \
  --arg codex_config_hash "$(
    [[ -f "${HOME}/.codex/config.toml" ]] \
      && sha256sum "${HOME}/.codex/config.toml" | awk '{print $1}' \
      || printf '%s' "missing"
  )" \
  '{
    generated_at: $generated_at,
    scope: "pre-migration",
    runtime_configuration_changed: false,
    hashes: {
      claude_settings: $claude_settings_hash,
      claude_marketplaces: $claude_marketplaces_hash,
      codex_config: $codex_config_hash,
      codex_local_plugins: $codex_plugins_hash
    },
    evidence: {
      claude_plugin_list: "raw/claude-plugin-list.json",
      codex_plugin_list: "raw/codex-plugin-list.json",
      manifest_paths: "raw/manifest-paths.txt"
    }
  }' >"${run_dir}/inventory.json"

printf 'Inventory: %s\n' "${run_dir}/inventory.json"
printf 'Backups: %s\n' "${backup_dir}"
