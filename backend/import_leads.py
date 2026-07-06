"""
import_leads.py  —  Restaurant Agency Platform
------------------------------------------------
Reads enriched_leads.json produced by Agent2, registers each business
with the FastAPI backend via POST /api/clients/register, and writes a
demo_links.json mapping business name → live demo URL.

Agent2 field  →  API field mapping is explicit below so it's easy to
extend when Agent2 adds new fields.

Run locally:
    python import_leads.py

Against Railway:
    BACKEND_API_URL=https://your-api.railway.app/api/clients/register \
    python import_leads.py
"""

import json
import os
import time
from pathlib import Path

import requests

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent          # dentist-website/ root
SHARED_DIR = BASE_DIR / "shared_data"
LEADS_FILE = SHARED_DIR / "enriched_leads.json"
OUTPUT_FILE = SHARED_DIR / "demo_links.json"
FAILED_FILE = SHARED_DIR / "failed_leads.json"

# ── Config ───────────────────────────────────────────────────────────────────
API_URL = os.getenv(
    "BACKEND_API_URL",
    "http://localhost:8000/api/clients/register",
)
SLEEP_BETWEEN_REQUESTS = 0.3   # seconds — be polite to the backend


# ── Niche normalisation ───────────────────────────────────────────────────────
def normalise_niche(raw: str | None) -> str:
    """
    Agent2 gives plural niche strings like 'dentists', 'restaurants'.
    The backend expects singular: 'dentist', 'restaurant'.
    We also map common variants so demo_seed.py can detect cuisine.
    """
    if not raw:
        return "restaurant"

    mapping = {
        "dentists":    "dentist",
        "restaurants": "restaurant",
        "cafes":       "cafe",
        "cafés":       "cafe",
        "bakeries":    "bakery",
        "bakery":      "cafe",          # demo_seed detects "cafe" keyword
        "pizzerias":   "restaurant",
        "pizzeria":    "restaurant",
        "bars":        "bar",
        "gyms":        "gym",
        "salons":      "salon",
        "spas":        "spa",
    }
    normalised = mapping.get(raw.lower().strip(), raw.lower().strip())

    # Strip trailing 's' as a last resort (catches most plurals)
    if normalised.endswith("s") and normalised not in {"business", "address"}:
        normalised = normalised[:-1]

    return normalised


def clean_address(raw: str | None) -> str | None:
    """Strip leading newlines / extra whitespace from Agent2 addresses."""
    if not raw:
        return None
    return raw.replace("\n", " ").strip() or None


def build_payload(lead: dict) -> dict:
    """
    Map every Agent2 field to the ClientCreate schema.
    Fields the backend doesn't know about are simply omitted.
    All optional fields default to None — the backend/frontend both
    handle missing values gracefully via fallbacks.
    """
    payload = {
        "business_name": (lead.get("name") or "").strip(),
        "niche":         normalise_niche(lead.get("niche")),
        "phone":         lead.get("phone"),
        "address":       clean_address(lead.get("address")),
        "email":         lead.get("email"),          # often null — that's fine
        "city":          lead.get("city"),
        "state":         lead.get("state"),
        "rating":        lead.get("lead_stage"),     # e.g. "85%"
        "google_maps_url": lead.get("maps_url"),
        "facebook_url":  lead.get("facebook_url"),
        "instagram_url": lead.get("instagram_url"),
        "lead_score":    lead.get("lead_stage"),
        "latitude":      lead.get("latitude"),
        "longitude":     lead.get("longitude"),
    }

    # Drop keys whose value is None or empty string so the backend
    # uses its own column defaults rather than storing empty strings.
    return {k: v for k, v in payload.items() if v not in (None, "", [])}


def main() -> None:
    if not LEADS_FILE.exists():
        print(f"❌  Leads file not found: {LEADS_FILE}")
        return

    with open(LEADS_FILE, encoding="utf-8") as f:
        leads: list[dict] = json.load(f)

    if not leads:
        print("⚠️  No leads found in file.")
        return

    print(f"📥  Found {len(leads)} leads — registering against {API_URL}")

    mapping: dict[str, str] = {}   # business_name → demo_url  (success)
    failures: list[dict]    = []   # raw leads that failed

    for lead in leads:
        name = (lead.get("name") or "").strip()
        if not name:
            print("  ⚠️  Skipping lead with no name.")
            continue

        payload = build_payload(lead)

        try:
            resp = requests.post(API_URL, json=payload, timeout=15)

            if resp.status_code == 200:
                data = resp.json()
                demo_url  = data.get("demo_url", "")
                slug      = data.get("slug", "")
                mapping[slug] = demo_url          # key by slug (stable, unique)
                print(f"  ✅  {name}  →  {demo_url}")

            else:
                print(f"  ❌  {name}  —  HTTP {resp.status_code}: {resp.text[:120]}")
                failures.append(lead)

        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  {name}  —  Cannot reach backend. Is it running?")
            failures.append(lead)
            break   # No point retrying every lead if backend is down

        except Exception as exc:
            print(f"  ⚠️  {name}  —  Unexpected error: {exc}")
            failures.append(lead)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # ── Write outputs ─────────────────────────────────────────────────────────
    SHARED_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"\n✅  Saved {len(mapping)} demo links → {OUTPUT_FILE}")

    if failures:
        with open(FAILED_FILE, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
        print(f"⚠️  {len(failures)} failed leads saved → {FAILED_FILE}")
    else:
        print("🎉  All leads registered successfully.")


if __name__ == "__main__":
    main()