import os
import sys
from datetime import datetime, timezone

import requests

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MESSAGE_ID = os.environ.get("MESSAGE_ID", "").strip()
SERVER = "malls-usability.tun.ply.gg"


def get_status():
    try:
        r = requests.get(f"https://api.mcstatus.io/v2/status/java/{SERVER}", timeout=15)
        return r.json()
    except Exception:
        return {"online": False}


def build_embed(data):
    online = data.get("online", False)
    players = data.get("players", {})
    fields = [
        {"name": "IP", "value": f"`{SERVER}`", "inline": False},
        {"name": "Version", "value": "Java 1.21.1", "inline": True},
        {
            "name": "Players",
            "value": f"{players.get('online', 0)} / {players.get('max', 20)}" if online else "N/A",
            "inline": True,
        },
    ]
    version = (data.get("version") or {}).get("name_clean")
    if online and version:
        fields[1]["value"] = f"Java {version}"
    names = [p["name_clean"] for p in players.get("list", [])] if online else []
    if names:
        fields.append({"name": "Online now", "value": ", ".join(names), "inline": False})

    return {
        "title": "All The Mods 10",
        "description": "🟢 Online" if online else "🔴 Offline",
        "color": 0x57F287 if online else 0xED4245,
        "fields": fields,
        "footer": {"text": "Last updated"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    embed = build_embed(get_status())

    if not MESSAGE_ID:
        r = requests.post(WEBHOOK_URL + "?wait=true", json={"embeds": [embed]}, timeout=15)
        r.raise_for_status()
        print("Posted. Save this as your MESSAGE_ID:", r.json()["id"])
        return

    r = requests.patch(
        f"{WEBHOOK_URL}/messages/{MESSAGE_ID}", json={"embeds": [embed]}, timeout=15
    )
    print("Edit status:", r.status_code)
    if r.status_code >= 400:
        sys.exit(1)


if __name__ == "__main__":
    main()
