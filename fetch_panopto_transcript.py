#!/usr/bin/env python3
"""
Fetch Panopto lecture transcripts and write them to files.

AUTH (cookie approach — works for students, no API client needed):
  1. Log into Panopto in your browser (through your school SSO).
  2. Open DevTools -> Application/Storage -> Cookies -> your Panopto domain.
  3. Copy the value of the `.ASPXAUTH` cookie (and `PanoptoMembershipCookie`
     if present). Easiest: DevTools -> Network -> click any request ->
     Request Headers -> copy the entire `Cookie:` header value.
  4. Put it in a .env file next to this script (see .env.example):
       PANOPTO_SERVER=yourschool.hosted.panopto.com
       PANOPTO_COOKIE=<the whole Cookie header value>

USAGE:
  # Single session by its viewer id (the id= in .../Viewer.aspx?id=<...>)
  python fetch_panopto_transcript.py <delivery-id> [output_dir]

  # All sessions in a folder
  python fetch_panopto_transcript.py --folder <folder-id> [output_dir]
"""

import os
import re
import sys
import pathlib
import urllib.parse
import requests


def load_dotenv(path=".env"):
    """Minimal .env loader: KEY=VALUE per line, # comments, optional quotes."""
    env_path = pathlib.Path(__file__).parent / path
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)


load_dotenv()

SERVER = os.environ.get("PANOPTO_SERVER", "").strip().rstrip("/")
COOKIE = os.environ.get("PANOPTO_COOKIE", "").strip()

if not SERVER or not COOKIE:
    sys.exit("Set PANOPTO_SERVER and PANOPTO_COOKIE in a .env file (see .env.example).")

BASE = f"https://{SERVER}/Panopto"
session = requests.Session()
session.headers.update({"Cookie": COOKIE, "User-Agent": "transcript-fetcher/1.0"})

# Data.svc (the endpoint the web UI uses) needs the CSRF token echoed back as a
# header. Pull it out of the cookie we were given and URL-decode it.
_m = re.search(r"csrfToken=([^;]+)", COOKIE)
if _m:
    session.headers["X-CSRF-Token"] = urllib.parse.unquote(_m.group(1))


def safe_name(s: str) -> str:
    return re.sub(r"[^\w\-. ]", "_", s).strip() or "untitled"


def srt_to_text(srt: str) -> str:
    """Strip SRT cue numbers + timestamps, leaving flowing transcript text."""
    parts = []
    for line in srt.splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        parts.append(line)
    return " ".join(parts)


def fetch_transcript(delivery_id: str) -> str:
    """Return the SRT transcript text for one session, or '' if none exists."""
    url = f"{BASE}/Pages/Transcription/GenerateSRT.ashx"
    r = session.get(url, params={"id": delivery_id, "language": "0"})
    r.raise_for_status()
    text = r.text
    # No captions -> Panopto returns empty or an HTML login page.
    if not text.strip() or text.lstrip().lower().startswith("<!doctype"):
        return ""
    return text


def session_title(delivery_id: str) -> str:
    """Best-effort human title via the public REST API; falls back to the id."""
    try:
        r = session.get(f"{BASE}/api/v1/sessions/{delivery_id}")
        if r.ok:
            return r.json().get("Name", delivery_id)
    except requests.RequestException:
        pass
    return delivery_id


def list_folder_sessions(folder_id: str) -> list[dict]:
    """Page through every session in a folder via the web UI's Data.svc endpoint.

    Returns dicts normalized to {"Id": deliveryId, "Name": title}. The public
    /api/v1 REST API needs an OAuth bearer token, but Data.svc/GetSessions
    accepts our session cookie + CSRF header, same as the browser.
    """
    out, page = [], 0
    while True:
        body = {
            "queryParameters": {
                "folderID": folder_id,
                "page": page,
                "maxResults": 50,
                "sortColumn": 1,
                "sortAscending": True,
                "getFolderData": True,
                "includePlaylists": True,
                "includeArchived": True,
                "query": None,
                "startDate": None,
                "endDate": None,
            }
        }
        r = session.post(f"{BASE}/Services/Data.svc/GetSessions", json=body)
        r.raise_for_status()
        results = r.json().get("d", {}).get("Results", []) or []
        if not results:
            break
        for s in results:
            out.append({"Id": s.get("DeliveryID"), "Name": s.get("SessionName")})
        page += 1
    return out


def write_one(delivery_id: str, out_dir: pathlib.Path, name: str | None = None):
    name = name or session_title(delivery_id)
    srt = fetch_transcript(delivery_id)
    if not srt:
        print(f"  ! no transcript for {name} ({delivery_id})")
        return
    path = out_dir / f"{safe_name(name)}.txt"
    path.write_text(srt_to_text(srt), encoding="utf-8")
    print(f"  + {path}")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    if args[0] == "--folder":
        folder_id = args[1]
        out_dir = pathlib.Path(args[2] if len(args) > 2 else "transcripts")
        out_dir.mkdir(parents=True, exist_ok=True)
        sessions = list_folder_sessions(folder_id)
        print(f"Found {len(sessions)} sessions in folder {folder_id}")
        for s in sessions:
            write_one(s["Id"], out_dir, s.get("Name"))
    else:
        delivery_id = args[0]
        out_dir = pathlib.Path(args[1] if len(args) > 1 else "transcripts")
        out_dir.mkdir(parents=True, exist_ok=True)
        write_one(delivery_id, out_dir)


if __name__ == "__main__":
    main()
