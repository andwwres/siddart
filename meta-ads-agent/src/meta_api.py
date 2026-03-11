"""Meta Marketing API client — executes tool calls against the Graph API."""

from __future__ import annotations

import json
import os

import httpx

BASE_URL = "https://graph.facebook.com"


def _version() -> str:
    return os.getenv("META_API_VERSION", "v21.0")


def _token() -> str:
    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN is not set")
    return token


def _normalize_account_id(account_id: str) -> str:
    """Ensure account_id has the act_ prefix."""
    if not account_id.startswith("act_"):
        return f"act_{account_id}"
    return account_id


def _get(path: str, params: dict | None = None) -> dict:
    params = params or {}
    params["access_token"] = _token()
    url = f"{BASE_URL}/{_version()}/{path}"
    resp = httpx.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, data: dict | None = None) -> dict:
    data = data or {}
    data["access_token"] = _token()
    url = f"{BASE_URL}/{_version()}/{path}"
    resp = httpx.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


INSIGHT_FIELDS = "spend,impressions,ctr,cpc,purchase_roas,actions"


# ── Tool handlers ────────────────────────────────────────────────────────────


def list_ad_accounts(business_id: str) -> str:
    data = _get(
        f"{business_id}/owned_ad_accounts",
        {"fields": "id,name,account_status", "limit": "100"},
    )
    accounts = data.get("data", [])
    if not accounts:
        return "No se encontraron cuentas de ads para este Business Manager."
    lines = [f"- **{a['name']}** (`{a['id']}`) — status: {a.get('account_status')}" for a in accounts]
    return f"Se encontraron {len(accounts)} cuentas:\n" + "\n".join(lines)


def get_account_insights(account_id: str, date_preset: str = "last_30d") -> str:
    aid = _normalize_account_id(account_id)
    data = _get(f"{aid}/insights", {"fields": INSIGHT_FIELDS, "date_preset": date_preset})
    rows = data.get("data", [])
    if not rows:
        return f"Sin datos de insights para {aid} en {date_preset}."
    return json.dumps(rows[0], indent=2)


def list_campaigns(account_id: str, status: str = "ACTIVE") -> str:
    aid = _normalize_account_id(account_id)
    params = {
        "fields": "id,name,status,objective,daily_budget",
        "filtering": json.dumps([{"field": "status", "operator": "EQUAL", "value": status}]),
        "limit": "100",
    }
    data = _get(f"{aid}/campaigns", params)
    campaigns = data.get("data", [])
    if not campaigns:
        return f"No hay campañas con status {status} en {aid}."
    lines = [
        f"- **{c['name']}** (`{c['id']}`) — {c.get('objective', 'N/A')} — budget: ${int(c.get('daily_budget', 0)) / 100:.2f}/day"
        for c in campaigns
    ]
    return f"{len(campaigns)} campañas {status}:\n" + "\n".join(lines)


def get_campaign_insights(campaign_id: str, date_preset: str = "last_30d") -> str:
    data = _get(f"{campaign_id}/insights", {"fields": INSIGHT_FIELDS, "date_preset": date_preset})
    rows = data.get("data", [])
    if not rows:
        return f"Sin datos de insights para campaña {campaign_id} en {date_preset}."
    return json.dumps(rows[0], indent=2)


def list_adsets(campaign_id: str) -> str:
    data = _get(
        f"{campaign_id}/adsets",
        {"fields": "id,name,status,daily_budget,targeting", "limit": "100"},
    )
    adsets = data.get("data", [])
    if not adsets:
        return f"No hay ad sets en la campaña {campaign_id}."
    lines = []
    for a in adsets:
        budget = f"${int(a.get('daily_budget', 0)) / 100:.2f}/day" if a.get("daily_budget") else "N/A"
        lines.append(f"- **{a['name']}** (`{a['id']}`) — {a.get('status')} — budget: {budget}")
    return f"{len(adsets)} ad sets:\n" + "\n".join(lines)


def update_campaign_budget(campaign_id: str, daily_budget_usd: float) -> str:
    budget_cents = int(daily_budget_usd * 100)
    _post(campaign_id, {"daily_budget": str(budget_cents)})
    return f"Presupuesto de campaña {campaign_id} actualizado a ${daily_budget_usd:.2f}/día."


def generate_account_report(account_id: str, date_preset: str = "last_30d") -> str:
    aid = _normalize_account_id(account_id)
    # Account-level insights
    acct_data = _get(f"{aid}/insights", {"fields": INSIGHT_FIELDS, "date_preset": date_preset})
    acct_rows = acct_data.get("data", [])

    # Campaign breakdown
    camp_data = _get(
        f"{aid}/insights",
        {"fields": INSIGHT_FIELDS, "date_preset": date_preset, "level": "campaign", "limit": "50"},
    )
    camp_rows = camp_data.get("data", [])

    report = {"account_id": aid, "date_preset": date_preset, "account_totals": acct_rows[0] if acct_rows else {}, "campaigns": camp_rows}
    return json.dumps(report, indent=2)


def _extract_purchases(actions: list | None) -> int:
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == "purchase":
            return int(a.get("value", 0))
    return 0


def show_accounts_dashboard(account_ids: list[str], date_preset: str = "last_30d") -> str:
    header = "| Account | Spend | Impressions | CTR | CPC | ROAS | Purchases |"
    sep = "|---------|-------|-------------|-----|-----|------|-----------|"
    rows = [header, sep]
    for aid in account_ids:
        aid = _normalize_account_id(aid)
        try:
            data = _get(f"{aid}/insights", {"fields": INSIGHT_FIELDS, "date_preset": date_preset})
            r = data.get("data", [{}])[0] if data.get("data") else {}
            purchases = _extract_purchases(r.get("actions"))
            roas_list = r.get("purchase_roas", [])
            roas = roas_list[0].get("value", "N/A") if roas_list else "N/A"
            rows.append(
                f"| {aid} | ${r.get('spend', '0')} | {r.get('impressions', '0')} | {r.get('ctr', 'N/A')}% | ${r.get('cpc', 'N/A')} | {roas} | {purchases} |"
            )
        except Exception as e:
            rows.append(f"| {aid} | Error: {e} | | | | | |")
    return "\n".join(rows)


def show_campaigns_dashboard(account_id: str, date_preset: str = "last_30d", status: str = "ACTIVE") -> str:
    aid = _normalize_account_id(account_id)
    data = _get(
        f"{aid}/insights",
        {
            "fields": f"campaign_id,campaign_name,{INSIGHT_FIELDS}",
            "date_preset": date_preset,
            "level": "campaign",
            "filtering": json.dumps([{"field": "campaign.delivery_info", "operator": "IN", "value": [status]}]),
            "limit": "50",
        },
    )
    campaigns = data.get("data", [])
    if not campaigns:
        return f"Sin campañas {status} con datos en {aid} para {date_preset}."

    header = "| Campaign | Spend | Impressions | CTR | CPC | ROAS | Purchases |"
    sep = "|----------|-------|-------------|-----|-----|------|-----------|"
    rows = [header, sep]
    for c in campaigns:
        purchases = _extract_purchases(c.get("actions"))
        roas_list = c.get("purchase_roas", [])
        roas = roas_list[0].get("value", "N/A") if roas_list else "N/A"
        rows.append(
            f"| {c.get('campaign_name', 'N/A')} | ${c.get('spend', '0')} | {c.get('impressions', '0')} | {c.get('ctr', 'N/A')}% | ${c.get('cpc', 'N/A')} | {roas} | {purchases} |"
        )
    return "\n".join(rows)


# ── Dispatcher ───────────────────────────────────────────────────────────────

HANDLERS = {
    "list_ad_accounts": lambda args: list_ad_accounts(**args),
    "get_account_insights": lambda args: get_account_insights(**args),
    "list_campaigns": lambda args: list_campaigns(**args),
    "get_campaign_insights": lambda args: get_campaign_insights(**args),
    "list_adsets": lambda args: list_adsets(**args),
    "update_campaign_budget": lambda args: update_campaign_budget(**args),
    "generate_account_report": lambda args: generate_account_report(**args),
    "show_accounts_dashboard": lambda args: show_accounts_dashboard(**args),
    "show_campaigns_dashboard": lambda args: show_campaigns_dashboard(**args),
}


def execute_tool(name: str, args: dict) -> str:
    handler = HANDLERS.get(name)
    if not handler:
        return f"Error: herramienta '{name}' no encontrada."
    try:
        return handler(args)
    except httpx.HTTPStatusError as e:
        return f"Error de la API de Meta ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error ejecutando {name}: {e}"
