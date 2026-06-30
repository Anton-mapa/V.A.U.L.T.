"""
Google Calendar integration for VAULT.
"""
# Python 3.14 enforces stricter cert checking that rejects some Google
# intermediate CAs. truststore injects the Windows certificate store so
# all HTTPS connections use the OS-trusted roots instead of certifi.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from datetime import datetime, timedelta
from pathlib import Path

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE       = Path(__file__).parent / "gcal_token.json"
SCOPES           = ["https://www.googleapis.com/auth/calendar.readonly"]
REDIRECT_URI     = "http://localhost:5000/api/gcal/callback"

# PKCE verifier keyed by OAuth state — survives the browser redirect
_pkce_store: dict = {}

KEYWORDS = [
    "examen", "parcial", "final", "tp", "trabajo práctico",
    "entrega", "actividad", "práctica", "quiz", "evaluación",
    "exam", "homework", "assignment", "test",
]


def _get_creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    if not TOKEN_FILE.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        return creds
    return None


def status():
    if not CREDENTIALS_FILE.exists():
        return {"connected": False, "needs_credentials": True}
    try:
        creds = _get_creds()
        if creds:
            return {"connected": True}
        return {"connected": False, "needs_auth": True}
    except Exception:
        return {"connected": False, "needs_auth": True}


def get_auth_url():
    from google_auth_oauthlib.flow import Flow

    if not CREDENTIALS_FILE.exists():
        return None, "credentials.json not found in vault-dashboard/"
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    url, state = flow.authorization_url(access_type="offline", prompt="consent")
    if getattr(flow, "code_verifier", None):
        _pkce_store[state] = flow.code_verifier
    return url, None


def handle_callback(code, state=None):
    from google_auth_oauthlib.flow import Flow

    if not CREDENTIALS_FILE.exists():
        return False, "credentials.json not found"
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    code_verifier = _pkce_store.pop(state, None) if state else None
    flow.fetch_token(code=code, code_verifier=code_verifier)
    TOKEN_FILE.write_text(flow.credentials.to_json(), encoding="utf-8")
    return True, None


def _matches(event):
    text = (event.get("summary", "") + " " + event.get("description", "")).lower()
    return any(kw in text for kw in KEYWORDS)


def _to_task(event):
    summary = event.get("summary", "Evento sin título")
    start   = event.get("start", {})
    due     = start.get("date") or (start.get("dateTime", "")[:10] if start.get("dateTime") else "")
    lower   = summary.lower()
    if any(k in lower for k in ["examen", "parcial", "final", "quiz", "evaluación", "test"]):
        category = "Examen"
    elif any(k in lower for k in ["tp", "trabajo práctico", "entrega", "homework", "assignment"]):
        category = "Tarea"
    else:
        category = "Actividad"
    return {
        "title":    summary,
        "category": category,
        "subject":  "",
        "due_date": due,
        "gcal_id":  event.get("id", ""),
    }


def sync_events(days_ahead=90):
    from googleapiclient.discovery import build

    creds = _get_creds()
    if not creds:
        return [], "Not authenticated — click Conectar in the sidebar"

    service  = build("calendar", "v3", credentials=creds)
    now      = datetime.utcnow()
    time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat() + "Z",
        timeMax=time_max,
        maxResults=250,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events  = result.get("items", [])
    matched = [_to_task(e) for e in events if _matches(e)]
    return matched, None
