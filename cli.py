#!/usr/bin/env python3
"""
cli.py - Command-line interface for testing the Sentiment Analysis Service.

Usage:
    python cli.py --text "I love this!"
    python cli.py --text "This is terrible." --url http://localhost:8080
    python cli.py --interactive
"""

import argparse
import json
import sys
import requests


DEFAULT_URL = "http://localhost:8080"


def predict(text: str, base_url: str) -> dict:
    """Send a prediction request to the service."""
    url = f"{base_url.rstrip('/')}/predict"
    try:
        response = requests.post(
            url,
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {url}. Is the service running?")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)


def print_result(result: dict):
    """Pretty-print prediction result."""
    sentiment = result.get("sentiment", "unknown").upper()
    score = result.get("score", 0.0)
    label = result.get("label", "")
    preview = result.get("text_preview", "")

    emoji = {"POSITIVE": "😊", "NEGATIVE": "😞", "NEUTRAL": "😐"}.get(sentiment, "❓")

    print("\n" + "=" * 50)
    print(f"  Sentiment : {emoji}  {sentiment}")
    print(f"  Model Label: {label}")
    print(f"  Confidence : {score * 100:.1f}%")
    print(f"  Input      : {preview}")
    print("=" * 50 + "\n")


def interactive_mode(base_url: str):
    """Run an interactive REPL for sentiment analysis."""
    print("\n🔍 Sentiment Analysis CLI — Interactive Mode")
    print("   Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            text = input("Enter text > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if text.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not text:
            continue

        result = predict(text, base_url)
        print_result(result)


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for the Sentiment Analysis Service"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of the service")
    parser.add_argument("--text", "-t", help="Text to analyze")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output raw JSON response"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.url)
    elif args.text:
        result = predict(args.text, args.url)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
