#!/usr/bin/env bash
#
# awesome_skills bootstrap installer.
#
#   curl -fsSL https://raw.githubusercontent.com/ash-hun/awesome_skills/main/install.sh | bash
#
# This script only clones (or updates) the repository, then hands the actual
# linking work over to bin/awesome-skills so that the logic lives in one place.
#
# Environment overrides:
#   AWESOME_SKILLS_REPO    git URL to clone from
#   AWESOME_SKILLS_HOME    where the clone lives (default: ~/.awesome-skills)
#   AWESOME_SKILLS_BRANCH  branch to track (default: main)

set -euo pipefail

REPO="${AWESOME_SKILLS_REPO:-https://github.com/ash-hun/awesome_skills.git}"
HOME_DIR="${AWESOME_SKILLS_HOME:-$HOME/.awesome-skills}"
BRANCH="${AWESOME_SKILLS_BRANCH:-main}"

die() { printf 'awesome_skills: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git is required but was not found in PATH."

if [ -d "$HOME_DIR/.git" ]; then
  printf 'Updating %s ...\n' "$HOME_DIR"
  git -C "$HOME_DIR" fetch --quiet origin "$BRANCH"
  git -C "$HOME_DIR" checkout --quiet "$BRANCH"
  git -C "$HOME_DIR" merge --quiet --ff-only "origin/$BRANCH"
elif [ -e "$HOME_DIR" ]; then
  die "$HOME_DIR already exists and is not a git clone. Move it aside and retry."
else
  printf 'Cloning %s into %s ...\n' "$REPO" "$HOME_DIR"
  git clone --quiet --branch "$BRANCH" "$REPO" "$HOME_DIR"
fi

[ -x "$HOME_DIR/bin/awesome-skills" ] || chmod +x "$HOME_DIR/bin/awesome-skills"

exec "$HOME_DIR/bin/awesome-skills" link
