#!/usr/bin/env bash
# Shared helpers: private GitHub token + clone/fetch without storing token in remote.
# Sourced by auto-update.sh / enable-auto-update.sh (not run directly).
# shellcheck shell=bash

STRATUM_DEFAULT_REPO_URL="${STRATUM_DEFAULT_REPO_URL:-https://github.com/alexanderponomarev-coder/digital-transformation-.git}"

stratum_load_git_env() {
  local f="${1:-/etc/stratum/stratum.env}"
  [[ -f "$f" ]] || return 0
  local line key val
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" =~ ^(STRATUM_GITHUB_TOKEN|GITHUB_TOKEN|STRATUM_GIT_DIR|STRATUM_GIT_REMOTE|STRATUM_GIT_BRANCH|STRATUM_REPO_URL|STRATUM_SERVER_NAME)=(.*)$ ]] || continue
    key="${BASH_REMATCH[1]}"
    val="${BASH_REMATCH[2]}"
    val="${val#\"}"
    val="${val%\"}"
    val="${val#\'}"
    val="${val%\'}"
    export "${key}=${val}"
  done <"$f"
}

stratum_public_repo_url() {
  local url="$1"
  if [[ "${url}" =~ ^https://x-access-token:[^@]+@github\.com/(.+)$ ]]; then
    printf 'https://github.com/%s' "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "${url}" =~ ^https://[^/@]+@github\.com/(.+)$ ]]; then
    printf 'https://github.com/%s' "${BASH_REMATCH[1]}"
    return 0
  fi
  printf '%s' "${url}"
}

# HTTPS URL with token in memory only (never write this to .git/config).
stratum_auth_repo_url() {
  local url="$1"
  local token="${STRATUM_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"
  url="$(stratum_public_repo_url "${url}")"
  if [[ -z "${token}" ]]; then
    printf '%s' "${url}"
    return 0
  fi
  if [[ "${url}" =~ ^https://github\.com/(.+)$ ]]; then
    printf 'https://x-access-token:%s@github.com/%s' "${token}" "${BASH_REMATCH[1]}"
    return 0
  fi
  printf '%s' "${url}"
}

# Clone into STRATUM_GIT_DIR if missing. Uses STRATUM_GITHUB_TOKEN for private HTTPS.
# Returns 0 on success / already present; 1 on failure.
stratum_ensure_git_clone() {
  local git_dir="${1:-${STRATUM_GIT_DIR:-/opt/stratum-src}}"
  local branch="${2:-${STRATUM_GIT_BRANCH:-main}}"
  local repo_url="${3:-${STRATUM_REPO_URL:-${STRATUM_DEFAULT_REPO_URL}}}"
  local token="${STRATUM_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"
  local log_fn="${4:-echo}"
  local auth_url tmp

  repo_url="$(stratum_public_repo_url "${repo_url}")"
  if [[ -d "${git_dir}/.git" ]]; then
    git -C "${git_dir}" remote set-url origin "${repo_url}" 2>/dev/null || true
    return 0
  fi

  if [[ -e "${git_dir}" && ! -d "${git_dir}/.git" ]]; then
    if [[ -n "$(ls -A "${git_dir}" 2>/dev/null || true)" ]]; then
      "${log_fn}" "ERROR: ${git_dir} существует без .git и не пуст — уберите каталог или укажите другой STRATUM_GIT_DIR"
      return 1
    fi
    rmdir "${git_dir}" 2>/dev/null || true
  fi

  auth_url="$(stratum_auth_repo_url "${repo_url}")"
  if [[ "${repo_url}" == https://github.com/* && -z "${token}" ]]; then
    "${log_fn}" "WARNING: клон private GitHub без STRATUM_GITHUB_TOKEN скорее всего упадёт"
  fi

  "${log_fn}" "git clone ${repo_url} → ${git_dir} (branch ${branch})"
  tmp="$(mktemp -d)"
  export GIT_TERMINAL_PROMPT=0
  if ! git clone --depth 50 --branch "${branch}" "${auth_url}" "${tmp}/repo"; then
    "${log_fn}" "ERROR: git clone не удался (auth? network?). Для private: STRATUM_GITHUB_TOKEN в /etc/stratum/stratum.env"
    rm -rf "${tmp}"
    return 1
  fi
  # origin без токена на диске
  git -C "${tmp}/repo" remote set-url origin "${repo_url}"
  mkdir -p "$(dirname "${git_dir}")"
  mv "${tmp}/repo" "${git_dir}"
  rm -rf "${tmp}"
  "${log_fn}" "клон готов: ${git_dir} (origin без токена)"
  return 0
}
