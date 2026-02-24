<p align="center">
  <strong>API for Chads</strong><br>
  <em>MCP server for AI agents — crypto prices, prediction markets, web research & rendering</em>
</p>

<p align="center">
  <a href="https://apiforchads.com">Website</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#tools">Tools</a> •
  <a href="#examples">Examples</a> •
  <a href="#payment">Payment</a>
</p>

<p align="center">
  <a href="https://smithery.ai/servers/chadbot0x/apiforchads"><img src="https://smithery.ai/badge/chadbot0x/apiforchads" alt="Smithery"></a>
  <img src="https://img.shields.io/badge/MCP-compatible-blue" alt="MCP Compatible">
  <img src="https://img.shields.io/badge/payment-x402_Solana-purple" alt="x402 Solana">
  <img src="https://img.shields.io/badge/tools-9-green" alt="9 Tools">
  <img src="https://img.shields.io/github/license/chadbot0x/apiforchads-mcp" alt="License">
  <img src="https://img.shields.io/github/last-commit/chadbot0x/apiforchads-mcp" alt="Last Commit">
</p>

---

**9 tools** for market intelligence, web rendering, and deep research. No accounts, no subscriptions — pay per request with Solana micropayments or an API key.

🌐 **[apiforchads.com](https://apiforchads.com)**

## Why?

AI agents need data. Getting it usually means API keys, monthly plans, rate limit dashboards, and billing pages. That's friction built for humans, not agents.

API for Chads is built for the agentic web:
- **MCP native** — agents discover and use tools automatically
- **x402 native** — agents pay per request with Solana, no human needed
- **One server, four capabilities** — prices, markets, research, rendering
- **Sub-penny pricing** — most requests cost < $0.02

## Tools

| Tool | What It Does | Price |
|------|-------------|-------|
| `get_crypto_price` | Real-time BTC/ETH via Chainlink oracles + Binance | 0.0001 SOL |
| `get_prediction_market` | Polymarket CLOB best bid/ask/spread | 0.0001 SOL |
| `quick_research` | Web-grounded research report (~20s) | 0.005 SOL |
| `deep_research` | Autonomous deep research with citations (~5min) | 0.02 SOL |
| `render_webpage` | JS-rendered page → markdown/text/html | 0.0003 SOL |
| `screenshot_webpage` | Full-page PNG screenshot | 0.0005 SOL |
| `extract_from_webpage` | CSS selector extraction from any page | 0.0003 SOL |
| `webpage_to_pdf` | Page → PDF document | 0.0005 SOL |
| `list_services` | Service catalog with pricing | Free |

## Quick Start

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "apiforchads": {
      "url": "https://mcp.apiforchads.com/mcp"
    }
  }
}
```

Restart Claude. You now have 9 new tools.

### Cursor / Windsurf

Add to your MCP settings:

```json
{
  "apiforchads": {
    "url": "https://mcp.apiforchads.com/mcp"
  }
}
```

### Any MCP Client (Python)

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://mcp.apiforchads.com/mcp") as (r, w, _):
    async with ClientSession(r, w) as session:
        await session.initialize()

        # Get BTC price
        result = await session.call_tool("get_crypto_price", {"asset": "BTC"})
        print(result)  # {"chainlink_price": 65920.45, "binance_price": 65935.12, ...}
```

## Examples

### Get crypto prices

```bash
# With API key
curl -H "Authorization: Bearer YOUR_KEY" \
  https://price.apiforchads.com/v1/prices/BTC

# Response
{
  "asset": "BTC",
  "chainlink_price": 65920.45,
  "binance_price": 65935.12,
  "chainlink_age_seconds": 13,
  "timestamp": 1771833021
}
```

### Get Polymarket orderbook

```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  https://price.apiforchads.com/v1/clob/will-trump-deport-less-than-250000

# Response
{
  "market_slug": "will-trump-deport-less-than-250000",
  "best_bid": 0.42,
  "best_ask": 0.44,
  "spread": 0.02,
  "mid_price": 0.43
}
```

### Quick research

```bash
curl -X POST -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  https://research.apiforchads.com/v1/research \
  -d '{"query": "What are the latest Bitcoin ETF inflows?", "tier": "quick"}'

# Returns job_id — poll /v1/research/status/{job_id} for results
```

### Render a JS-heavy page

```bash
curl -X POST -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  https://render.apiforchads.com/v1/render \
  -d '{"url": "https://polymarket.com", "format": "markdown", "max_chars": 5000}'
```

### Screenshot

```bash
curl -X POST -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  https://render.apiforchads.com/v1/render/screenshot \
  -d '{"url": "https://example.com", "full_page": true}' \
  --output screenshot.png
```

### Python SDK (coming soon)

```python
from apiforchads import Client

client = Client(api_key="YOUR_KEY")

btc = client.price("BTC")
print(f"BTC: ${btc.chainlink_price:,.2f}")

market = client.clob("will-trump-deport-less-than-250000")
print(f"Bid: {market.best_bid} Ask: {market.best_ask}")

report = client.research("Latest crypto regulations", tier="quick")
print(report.text)
```

## Payment

Two ways to pay:

### 1. API Key (recommended for humans)

Get a free API key with 1000 requests: email **chadbot0x@proton.me**

```bash
curl -H "Authorization: Bearer YOUR_KEY" https://price.apiforchads.com/v1/prices/BTC
```

### 2. x402 Micropayments (for agents)

The [x402 protocol](https://x402.org) lets agents pay per request with Solana:

1. Call any endpoint — get a `402` with payment details
2. Send micropayment to `EDQQe7Nufgvo2A6uXTmCpTr2FumZRB3fNzTH4Wuvpvpd`
3. Retry with `X-Payment-Signature` header containing the tx signature
4. Get your data

No signup. No monthly fee. Pure pay-per-use.

## REST API Endpoints

Use these directly without MCP:

| Base URL | Service |
|----------|---------|
| `https://price.apiforchads.com` | Crypto prices + Polymarket CLOB |
| `https://research.apiforchads.com` | AI-powered research |
| `https://render.apiforchads.com` | Web rendering, screenshots, PDFs |
| `https://mcp.apiforchads.com` | MCP protocol endpoint |

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Price/CLOB | 60/min |
| Research | 10/min |
| Render | 30/min |

## Architecture

```
                    ┌─────────────────────┐
                    │   Cloudflare Edge    │
                    │   (SSL + routing)    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────┴──┐   ┌────────┴───┐   ┌────────┴───┐
    │ Price API  │   │ Research   │   │ Render API │
    │ :8100      │   │ API :8101  │   │ :8102      │
    │            │   │            │   │            │
    │ • Chainlink│   │ • Gemini   │   │ • Playwright│
    │ • Binance  │   │ • Google   │   │ • Chromium  │
    │ • CLOB     │   │ • Search   │   │ • SSRF prot │
    └────────────┘   └────────────┘   └────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   MCP Server :8103  │
                    │   (tool discovery)  │
                    └─────────────────────┘
```

## Built With

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — FastMCP streamable HTTP transport
- [Chainlink](https://chain.link) — decentralized oracle price feeds
- [Playwright](https://playwright.dev) — headless Chromium for JS rendering
- [Gemini](https://ai.google.dev) — AI research with Google Search grounding
- [x402](https://x402.org) — HTTP 402 micropayment protocol on Solana
- [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) — zero-trust networking

## Self-Hosting

```bash
git clone https://github.com/chadbot0x/apiforchads-mcp.git
cd apiforchads-mcp

# Install dependencies
pip install mcp httpx

# Run the MCP server (connects to public APIs by default)
python server.py
```

To run the full stack (price + research + render APIs), see the [self-hosting guide](https://apiforchads.com/docs/self-hosting) (coming soon).

## Contributing

Issues and PRs welcome. If you build something cool with these tools, let us know.

## License

[MIT](LICENSE)

---

<p align="center">
  Built by <a href="https://github.com/chadbot0x">@chadbot0x</a> · Powered by agents, for agents
</p>
