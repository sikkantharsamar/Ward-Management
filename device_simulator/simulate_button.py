"""Pretends to be a bedside button / wearable so the software team can test without hardware.

Usage:
    python simulate_button.py --key demo-key-bed-1
    python simulate_button.py --key demo-key-bed-1 --source wearable --url http://192.168.1.10:8000

It also shows the retry behaviour the real firmware must copy: keep retrying until the server
replies HTTP 200 (the ACK). Only standard-library modules are used.
"""
import argparse
import json
import time
import urllib.error
import urllib.request


def send_alert(url: str, key: str, source: str, max_attempts: int) -> bool:
    body = json.dumps({"source": source}).encode()
    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(
            url + "/api/alerts/device",
            data=body,
            headers={"Content-Type": "application/json", "X-Device-Key": key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                reply = json.loads(response.read().decode())
                print(f"ACK received on attempt {attempt}: {reply}")
                return True
        except urllib.error.HTTPError as err:
            print(f"Attempt {attempt}: server rejected the alert ({err.code}) {err.read().decode()}")
            if err.code in (401, 403):
                return False  # wrong key: retrying will not help
        except Exception as err:  # network down, server off, timeout
            print(f"Attempt {attempt}: no ACK ({err}). Local buzzer ON, alert kept in buffer.")
        time.sleep(min(2 * attempt, 10))
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate an emergency button press")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--key", required=True, help="device key of the bed")
    parser.add_argument("--source", default="bedside_button", choices=["bedside_button", "wearable"])
    parser.add_argument("--attempts", type=int, default=5)
    args = parser.parse_args()
    ok = send_alert(args.url.rstrip("/"), args.key, args.source, args.attempts)
    print("Alert delivered." if ok else "ALERT NOT DELIVERED - keep buzzer on and retry.")
