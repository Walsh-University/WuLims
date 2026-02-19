#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${WULIMS_REPO_URL:-https://github.com/Walsh-University/WuLims.git}"
TARGET_DIR="${WULIMS_DIR:-WuLims}"

log() {
  printf '\n==> %s\n' "$1"
}

err() {
  printf '\nERROR: %s\n' "$1" >&2
  exit 1
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "macos" ;;
    Linux) echo "linux" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *) echo "unknown" ;;
  esac
}

print_install_hint() {
  local tool="$1"
  local os="$2"

  case "$tool" in
    git)
      if [[ "$os" == "macos" ]]; then
        echo "Install Git (Xcode CLT): xcode-select --install"
      elif [[ "$os" == "linux" ]]; then
        echo "Install Git with your package manager (apt, dnf, pacman, etc.)."
      else
        echo "Install Git for Windows: https://git-scm.com/download/win"
      fi
      ;;
    docker)
      if [[ "$os" == "macos" || "$os" == "windows" ]]; then
        echo "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
      else
        echo "Install Docker Engine + Compose plugin for your Linux distro."
      fi
      ;;
    *)
      echo "Install '$tool' and retry."
      ;;
  esac
}

ensure_uv() {
  if has_cmd uv; then
    return
  fi

  log "Installing uv"
  if ! has_cmd curl; then
    err "curl is required to install uv. Install curl and re-run setup."
  fi

  curl -LsSf https://astral.sh/uv/install.sh | sh

  export PATH="$HOME/.local/bin:$PATH"
  has_cmd uv || err "uv installation completed, but 'uv' is not in PATH. Open a new shell and re-run."
}

ensure_repo() {
  if [[ -f "./manage.py" && -f "./scripts/setup_dev_env.py" ]]; then
    log "Using current directory as WuLims repository"
    return
  fi

  has_cmd git || err "git is not installed. $(print_install_hint git "$(detect_os)")"

  if [[ -d "$TARGET_DIR/.git" ]]; then
    log "Using existing repository at ./$TARGET_DIR"
  elif [[ -e "$TARGET_DIR" ]]; then
    err "Target path '$TARGET_DIR' exists and is not a git repository. Remove it or set WULIMS_DIR."
  else
    log "Cloning WuLims repository"
    git clone "$REPO_URL" "$TARGET_DIR"
  fi

  cd "$TARGET_DIR"
}

ensure_docker() {
  local os
  os="$(detect_os)"

  has_cmd docker || err "docker is not installed. $(print_install_hint docker "$os")"

  if ! docker info >/dev/null 2>&1; then
    err "Docker is installed but not running. Start Docker Desktop/Engine and re-run."
  fi
}

main() {
  log "WuLims one-step setup"

  ensure_repo
  ensure_uv
  ensure_docker

  log "Installing Python dependencies"
  uv sync

  log "Running project bootstrap"
  uv run python scripts/setup_dev_env.py

  log "Complete"
  echo "Start the app with:"
  echo "  cd $(pwd)"
  echo "  uv run python manage.py runserver"
}

main "$@"
