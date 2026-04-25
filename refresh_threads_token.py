import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


THREADS_REFRESH_URL = "https://graph.threads.net/refresh_access_token"
THREADS_EXCHANGE_URL = "https://graph.threads.net/access_token"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh or exchange a Threads access token."
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to the env file that stores THREADS_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--exchange-short-lived",
        action="store_true",
        help="Exchange the current short-lived token for a long-lived token.",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Token to use instead of THREADS_ACCESS_TOKEN from the env file.",
    )
    parser.add_argument(
        "--app-secret",
        default=None,
        help="Threads app secret. Required when exchanging a short-lived token.",
    )
    args = parser.parse_args()

    env_path = Path(args.env_file)
    load_dotenv(env_path)

    token = args.token or os.getenv("THREADS_ACCESS_TOKEN")
    if not token:
        raise SystemExit("THREADS_ACCESS_TOKEN is not set.")

    if args.exchange_short_lived:
        app_secret = args.app_secret or os.getenv("THREADS_APP_SECRET")
        if not app_secret:
            raise SystemExit(
                "THREADS_APP_SECRET is required to exchange a short-lived token."
            )
        data = exchange_short_lived_token(token, app_secret)
    else:
        data = refresh_long_lived_token(token)

    new_token = data["access_token"]
    expires_in = int(data.get("expires_in", 0))
    update_env_value(env_path, "THREADS_ACCESS_TOKEN", new_token)
    if expires_in:
        update_env_value(env_path, "THREADS_TOKEN_EXPIRES_IN", str(expires_in))

    days = round(expires_in / 86400, 1) if expires_in else "unknown"
    print(f"Updated THREADS_ACCESS_TOKEN in {env_path}. Expires in: {days} days")


def exchange_short_lived_token(token: str, app_secret: str) -> dict:
    response = requests.get(
        THREADS_EXCHANGE_URL,
        params={
            "grant_type": "th_exchange_token",
            "client_secret": app_secret,
            "access_token": token,
        },
        timeout=30,
    )
    return parse_token_response(response)


def refresh_long_lived_token(token: str) -> dict:
    response = requests.get(
        THREADS_REFRESH_URL,
        params={
            "grant_type": "th_refresh_token",
            "access_token": token,
        },
        timeout=30,
    )
    return parse_token_response(response)


def parse_token_response(response: requests.Response) -> dict:
    try:
        data = response.json()
    except ValueError as exc:
        raise SystemExit(f"Token endpoint returned non-JSON: {response.text}") from exc

    if not response.ok or "access_token" not in data:
        raise SystemExit(f"Token refresh failed: {data}")
    return data


def update_env_value(env_path: Path, key: str, value: str) -> None:
    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated = False
    output = []

    for line in lines:
        if line.startswith(f"{key}="):
            output.append(f"{key}={value}")
            updated = True
        else:
            output.append(line)

    if not updated:
        output.append(f"{key}={value}")

    env_path.write_text("\n".join(output) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
