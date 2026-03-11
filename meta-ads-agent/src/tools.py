"""Meta Ads MCP tool definitions for the Claude agent."""

TOOLS = [
    {
        "name": "list_ad_accounts",
        "description": (
            "Lista todas las cuentas de ads bajo un Meta Business Manager. "
            "Retorna id, nombre y estado de cada cuenta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "business_id": {
                    "type": "string",
                    "description": "ID del Meta Business Manager.",
                }
            },
            "required": ["business_id"],
        },
    },
    {
        "name": "get_account_insights",
        "description": (
            "Obtiene métricas de rendimiento de una cuenta de ads: "
            "spend, impressions, CTR, CPC, ROAS, purchases."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "ID de la cuenta de ads (con o sin prefijo act_).",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Período de tiempo.",
                    "enum": [
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "list_campaigns",
        "description": "Lista campañas de una cuenta de ads con su estado y objetivo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "ID de la cuenta de ads.",
                },
                "status": {
                    "type": "string",
                    "description": "Filtrar por estado.",
                    "enum": ["ACTIVE", "PAUSED", "ARCHIVED"],
                    "default": "ACTIVE",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_campaign_insights",
        "description": (
            "Métricas de rendimiento para una campaña específica: "
            "spend, impressions, CTR, CPC, ROAS, purchases."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "ID de la campaña.",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Período de tiempo.",
                    "enum": [
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "list_adsets",
        "description": "Lista ad sets de una campaña con targeting y presupuesto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "ID de la campaña.",
                }
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "update_campaign_budget",
        "description": (
            "Actualiza el presupuesto diario de una campaña. "
            "IMPORTANTE: siempre confirmar con el usuario antes de ejecutar."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "ID de la campaña.",
                },
                "daily_budget_usd": {
                    "type": "number",
                    "description": "Nuevo presupuesto diario en USD.",
                },
            },
            "required": ["campaign_id", "daily_budget_usd"],
        },
    },
    {
        "name": "generate_account_report",
        "description": (
            "Genera un reporte completo de rendimiento con todas las campañas "
            "de una cuenta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "ID de la cuenta de ads.",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Período de tiempo.",
                    "enum": [
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "show_accounts_dashboard",
        "description": (
            "Muestra una tabla markdown comparando métricas de múltiples cuentas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de IDs de cuentas de ads.",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Período de tiempo.",
                    "enum": [
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
            },
            "required": ["account_ids"],
        },
    },
    {
        "name": "show_campaigns_dashboard",
        "description": (
            "Muestra una tabla markdown con métricas por campaña de una cuenta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "ID de la cuenta de ads.",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Período de tiempo.",
                    "enum": [
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "default": "last_30d",
                },
                "status": {
                    "type": "string",
                    "description": "Filtrar por estado.",
                    "enum": ["ACTIVE", "PAUSED", "ARCHIVED"],
                    "default": "ACTIVE",
                },
            },
            "required": ["account_id"],
        },
    },
]
