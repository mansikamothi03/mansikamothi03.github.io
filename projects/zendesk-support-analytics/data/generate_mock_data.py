"""
generate_mock_data.py
---------------------
Generates a realistic mock Zendesk ticket dataset for analysis.
Run this script once to create data/raw/tickets.csv

Usage: python data/generate_mock_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# Config
N_TICKETS = 2000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

CATEGORIES = {
    "Billing & Invoicing": 0.22,
    "Authentication / SSO": 0.18,
    "Feature Request": 0.16,
    "Performance / Speed": 0.14,
    "Data Export / Import": 0.12,
    "Onboarding / Setup": 0.10,
    "Bug Report": 0.08,
}

PRIORITIES = {"urgent": 0.08, "high": 0.20, "normal": 0.55, "low": 0.17}
CHANNELS = {"email": 0.45, "web": 0.30, "chat": 0.15, "api": 0.10}
STATUSES = {"solved": 0.72, "closed": 0.15, "open": 0.08, "pending": 0.05}
ACCOUNT_TIERS = {"enterprise": 0.15, "pro": 0.40, "starter": 0.45}

AGENTS = [
    "Sarah Chen", "Marcus Williams", "Priya Patel",
    "James O'Brien", "Aisha Johnson", "Tom Nakamura",
]

SUBJECTS = {
    "Billing & Invoicing": [
        "Cannot find my invoice for last month",
        "Charged twice this billing cycle",
        "Need to update payment method",
        "Invoice PDF shows blank page",
        "Annual billing discount not applied",
    ],
    "Authentication / SSO": [
        "SSO login failing for entire team",
        "Cannot reset password — email not arriving",
        "2FA codes not working",
        "SAML configuration error",
        "Session expires too quickly",
    ],
    "Feature Request": [
        "Please add bulk CSV export",
        "Need Slack integration for alerts",
        "Request: scheduled email reports",
        "Dark mode for dashboard",
        "Python SDK for API access",
    ],
    "Performance / Speed": [
        "Dashboard loading takes 15+ seconds",
        "API response times degraded",
        "Report export timing out",
        "Slow search results",
        "Charts not rendering on large datasets",
    ],
    "Data Export / Import": [
        "CSV export missing columns",
        "Salesforce sync stopped working",
        "Import fails on files > 50MB",
        "Webhook firing duplicate events",
        "Data not refreshing after import",
    ],
    "Onboarding / Setup": [
        "Cannot connect data source during setup",
        "Onboarding checklist steps not working",
        "Documentation is outdated",
        "Need help with initial configuration",
        "Trial expired before setup complete",
    ],
    "Bug Report": [
        "Delete button does nothing",
        "Charts not rendering in Firefox",
        "Filters reset on page refresh",
        "Notifications not sending",
        "Search returns wrong results",
    ],
}


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def resolution_hours(priority: str, status: str) -> float:
    if status in ("open", "pending"):
        return None
    base = {"urgent": 3, "high": 8, "normal": 24, "low": 72}[priority]
    return round(max(0.5, np.random.lognormal(np.log(base), 0.6)), 1)


def first_reply_hours(priority: str) -> float:
    base = {"urgent": 1, "high": 3, "normal": 8, "low": 24}[priority]
    return round(max(0.1, np.random.lognormal(np.log(base), 0.5)), 1)


def csat_score(priority: str, resolution_h: float) -> str:
    if resolution_h is None:
        return None
    # Higher priority + faster resolution = more likely good CSAT
    good_prob = 0.78
    if priority == "urgent" and resolution_h > 8:
        good_prob = 0.35
    elif priority == "high" and resolution_h > 16:
        good_prob = 0.50
    return "good" if random.random() < good_prob else "bad"


rows = []
for i in range(1, N_TICKETS + 1):
    category = random.choices(list(CATEGORIES.keys()), weights=list(CATEGORIES.values()))[0]
    priority = random.choices(list(PRIORITIES.keys()), weights=list(PRIORITIES.values()))[0]
    channel = random.choices(list(CHANNELS.keys()), weights=list(CHANNELS.values()))[0]
    status = random.choices(list(STATUSES.keys()), weights=list(STATUSES.values()))[0]
    tier = random.choices(list(ACCOUNT_TIERS.keys()), weights=list(ACCOUNT_TIERS.values()))[0]
    subject = random.choice(SUBJECTS[category])
    created = random_date(START_DATE, END_DATE)
    res_h = resolution_hours(priority, status)
    reply_h = first_reply_hours(priority)
    solved_at = (created + timedelta(hours=res_h)) if res_h else None
    first_reply_at = created + timedelta(hours=reply_h)

    sla_limits = {"urgent": 4, "high": 8, "normal": 24, "low": 48}
    is_sla_breached = reply_h > sla_limits[priority]

    rows.append({
        "ticket_id": f"TKT-{i:05d}",
        "subject": subject,
        "category": category,
        "priority": priority,
        "channel": channel,
        "status": status,
        "account_tier": tier,
        "agent": random.choice(AGENTS),
        "account_id": f"ACC-{random.randint(1000, 1200):04d}",
        "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        "solved_at": solved_at.strftime("%Y-%m-%d %H:%M:%S") if solved_at else None,
        "first_reply_at": first_reply_at.strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_hours": res_h,
        "first_reply_hours": round(reply_h, 1),
        "is_sla_breached": is_sla_breached,
        "csat_score": csat_score(priority, res_h),
    })

df = pd.DataFrame(rows)
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/tickets.csv", index=False)
print(f"Generated {len(df)} tickets → data/raw/tickets.csv")
print(df["category"].value_counts())