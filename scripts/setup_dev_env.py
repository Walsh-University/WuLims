#!/usr/bin/env python3
"""Bootstrap local development environment for WuLims on macOS/Windows."""

from __future__ import annotations

import getpass
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_EXAMPLE_PATH = ROOT_DIR / ".env.example"
ENV_PATH = ROOT_DIR / ".env"
COMPOSE_FILE_PATH = ROOT_DIR / "docker" / "docker-compose.yml"


def print_step(message: str) -> None:
    print(f"\n==> {message}")


def fail(message: str, code: int = 1) -> None:
    print(f"\nERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def run_command(command: list[str], env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    return subprocess.run(command, cwd=ROOT_DIR, env=env, text=True, check=check)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def load_env_file(path: Path) -> dict[str, str]:
    env_data: dict[str, str] = {}
    if not path.exists():
        return env_data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_data[key.strip()] = value.strip().strip("\"'")
    return env_data


def copy_env_file_if_needed() -> None:
    if ENV_PATH.exists():
        print_step(".env already exists, skipping copy from .env.example")
        return
    if not ENV_EXAMPLE_PATH.exists():
        fail("Missing .env.example; cannot create .env")
    shutil.copy2(ENV_EXAMPLE_PATH, ENV_PATH)
    print_step("Copied .env.example to .env")


def get_compose_command(env: dict[str, str]) -> list[str]:
    if command_exists("docker"):
        probe = subprocess.run(["docker", "compose", "version"], cwd=ROOT_DIR, env=env, text=True)
        if probe.returncode == 0:
            return ["docker", "compose"]
    if command_exists("docker-compose"):
        probe = subprocess.run(["docker-compose", "--version"], cwd=ROOT_DIR, env=env, text=True)
        if probe.returncode == 0:
            return ["docker-compose"]
    fail("Docker Compose is not available. Install Docker Desktop and try again.")
    return []


def get_manage_command() -> list[str]:
    if command_exists("uv"):
        return ["uv", "run", "python", "manage.py"]
    if command_exists("python"):
        return ["python", "manage.py"]
    if os.name == "nt" and command_exists("py"):
        return ["py", "manage.py"]
    fail("No Python runtime found. Install Python (or uv) and try again.")
    return []


def install_pre_commit(env: dict[str, str]) -> None:
    print_step("Installing pre-commit hooks")
    if command_exists("uv"):
        run_command(["uv", "run", "pre-commit", "install"], env=env)
        return
    if command_exists("pre-commit"):
        run_command(["pre-commit", "install"], env=env)
        return
    fail("pre-commit is not available. Run dependency installation first (e.g., `uv sync`).")


def start_postgres(compose_command: list[str], env: dict[str, str]) -> None:
    print_step("Starting PostgreSQL container")
    run_command([*compose_command, "-f", str(COMPOSE_FILE_PATH), "up", "-d", "db"], env=env)


def run_migrations_with_retry(
    manage_command: list[str], env: dict[str, str], retries: int = 30, wait_seconds: int = 2
) -> None:
    print_step("Running migrations")
    for attempt in range(1, retries + 1):
        result = subprocess.run(
            [*manage_command, "migrate", "--noinput"],
            cwd=ROOT_DIR,
            env=env,
            text=True,
        )
        if result.returncode == 0:
            print("Migrations complete.")
            return
        print(f"Migration attempt {attempt}/{retries} failed; waiting {wait_seconds}s for DB readiness...")
        time.sleep(wait_seconds)
    fail("Could not run migrations after multiple attempts.")


def prompt_superuser_details(defaults: dict[str, str]) -> tuple[str, str, str]:
    print_step("Creating Django superuser")

    default_username = defaults.get("DJANGO_SUPERUSER_USERNAME", "admin")
    default_email = defaults.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

    username = input(f"Superuser username [{default_username}]: ").strip() or default_username
    email = input(f"Superuser email [{default_email}]: ").strip() or default_email

    while True:
        password = getpass.getpass("Superuser password: ")
        confirm = getpass.getpass("Confirm superuser password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        if password != confirm:
            print("Passwords do not match. Try again.")
            continue
        return username, email, password


def create_or_update_superuser(
    manage_command: list[str], env: dict[str, str], username: str, email: str, password: str
) -> None:
    python_code = (
        "from django.contrib.auth import get_user_model;"
        "import os;"
        "User=get_user_model();"
        "username=os.environ['DJANGO_SUPERUSER_USERNAME'];"
        "email=os.environ['DJANGO_SUPERUSER_EMAIL'];"
        "password=os.environ['DJANGO_SUPERUSER_PASSWORD'];"
        "obj,created=User.objects.get_or_create(username=username,defaults={'email':email,'is_staff':True,'is_superuser':True});"
        "obj.email=email;obj.is_staff=True;obj.is_superuser=True;obj.set_password(password);obj.save();"
        "print(('Created' if created else 'Updated') + f' superuser: {username}')"
    )

    superuser_env = dict(env)
    superuser_env["DJANGO_SUPERUSER_USERNAME"] = username
    superuser_env["DJANGO_SUPERUSER_EMAIL"] = email
    superuser_env["DJANGO_SUPERUSER_PASSWORD"] = password

    run_command([*manage_command, "shell", "-c", python_code], env=superuser_env)


def main() -> None:
    print_step("WuLims development environment bootstrap")

    copy_env_file_if_needed()

    env_from_file = load_env_file(ENV_PATH)
    env = dict(os.environ)
    env.update(env_from_file)

    install_pre_commit(env)
    compose_command = get_compose_command(env)
    start_postgres(compose_command, env)

    manage_command = get_manage_command()
    run_migrations_with_retry(manage_command, env)

    username, email, password = prompt_superuser_details(env_from_file)
    create_or_update_superuser(manage_command, env, username, email, password)

    print_step("Done")
    print("Environment setup complete. Start the app with:")
    print(f"$ {' '.join([*manage_command, 'runserver'])}")


if __name__ == "__main__":
    main()
