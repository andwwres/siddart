# Meta Ads Agent

Agente conversacional para gestionar campañas de Meta Ads (Facebook/Instagram) usando Claude como modelo de lenguaje.

## Capacidades

- Listar cuentas de ads de un Business Manager
- Consultar métricas de rendimiento (spend, impressions, CTR, CPC, ROAS, purchases)
- Listar campañas y ad sets
- Dashboards comparativos en formato markdown
- Actualizar presupuestos de campañas (con confirmación)
- Reportes completos de cuenta

## Setup

```bash
# Clonar e instalar
cd meta-ads-agent
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key de Anthropic |
| `META_ACCESS_TOKEN` | Token de acceso de Meta Marketing API |
| `META_BUSINESS_ID` | ID del Business Manager (opcional) |
| `META_API_VERSION` | Versión de la Graph API (default: v21.0) |
| `CLAUDE_MODEL` | Modelo de Claude a usar (default: claude-sonnet-4-20250514) |

## Uso

```bash
meta-ads-agent
```

### Ejemplos de consultas

- "Muéstrame todas las cuentas del business 123456789"
- "¿Cuál es el rendimiento de la cuenta act_987654321 en los últimos 7 días?"
- "Dame un dashboard de campañas activas de la cuenta act_123"
- "Actualiza el presupuesto de la campaña 555 a $50/día"
