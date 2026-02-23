# API for Chads — MCP Server

Pay-per-call AI agent services via [x402](https://x402.org) micropayments on Solana.

**9 tools** for market intelligence, web rendering, and deep research — no accounts, no subscriptions.

🌐 **https://apiforchads.com**

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `get_crypto_price` | Real-time crypto prices (Chainlink + Binance) | 0.0001 SOL |
| `get_prediction_market` | Polymarket CLOB best bid/ask | 0.0001 SOL |
| `quick_research` | Web-grounded research report (~20s) | 0.005 SOL |
| `deep_research` | Full cited research report (~5min) | 0.02 SOL |
| `render_webpage` | JS-rendered page → markdown/text/html | 0.0003 SOL |
| `screenshot_webpage` | Full-page PNG screenshot | 0.0005 SOL |
| `extract_from_webpage` | CSS selector extraction | 0.0003 SOL |
| `webpage_to_pdf` | Page → PDF document | 0.0005 SOL |
| `list_services` | Full service catalog with pricing | Free |

## Quick Start

### Connect via Streamable HTTP

MCP endpoint: `https://mcp.apiforchads.com/mcp`

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "apiforchads": {
      "url": "https://mcp.apiforchads.com/mcp"
    }
  }
}
```

### Any MCP Client

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://mcp.apiforchads.com/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("get_crypto_price", {"asset": "BTC"})
```

## Payment

All paid endpoints use the [x402 protocol](https://x402.org):

1. Call any tool — if payment is required, you get a 402 with Solana payment details
2. Send the micropayment on Solana
3. Retry with `X-Payment-Signature` header
4. Get your data

**Recipient:** `EDQQe7Nufgvo2A6uXTmCpTr2FumZRB3fNzTH4Wuvpvpd`

Or use an API key for bulk access (contact us).

## API Endpoints

Direct REST access (without MCP):

- **Price:** https://price.apiforchads.com
- **Research:** https://research.apiforchads.com  
- **Render:** https://render.apiforchads.com

## Built With

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (FastMCP)
- [Playwright](https://playwright.dev) for web rendering
- [Gemini](https://ai.google.dev) for research
- [Chainlink](https://chain.link) for oracle prices
- [x402](https://x402.org) for payments

## License

MIT
