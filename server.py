#!/usr/bin/env python3
"""
API for Chads — MCP Server
Wraps all x402 services (price, research, render) as MCP tools.
Discoverable by Claude, GPT, and any MCP-compatible agent.

Supports both stdio and Streamable HTTP transports.
Run:
  stdio:  python3 mcp_server.py
  http:   python3 mcp_server.py --http --port 8103
"""

import json
import os
import sys
import urllib.request
import urllib.error

from mcp.server.fastmcp import FastMCP

# ─── Config ──────────────────────────────────────────────────────────────────

PRICE_API = os.environ.get("PRICE_API_URL", "http://localhost:8100")
RESEARCH_API = os.environ.get("RESEARCH_API_URL", "http://localhost:8101")
RENDER_API = os.environ.get("RENDER_API_URL", "http://localhost:8102")

# Internal API key for MCP server → backend calls (no x402 payment needed internally)
API_KEY = os.environ.get("MCP_API_KEY", "")

# Load from secrets if not in env
if not API_KEY:
    try:
        with open("/Users/jm/.openclaw/.secrets/api-keys.json") as f:
            keys = json.load(f)
            API_KEY = list(keys.keys())[0] if keys else ""
    except Exception:
        pass

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _request(method: str, url: str, body: dict = None) -> dict:
    """Make HTTP request to backend API."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            return {"error": json.loads(error_body)}
        except Exception:
            return {"error": {"status": e.code, "message": error_body[:500]}}
    except Exception as e:
        return {"error": {"message": str(e)[:500]}}


def _poll_research(job_id: str, max_wait: int = 300) -> dict:
    """Poll research job until completion."""
    import time
    start = time.time()
    while time.time() - start < max_wait:
        status = _request("GET", f"{RESEARCH_API}/v1/research/status/{job_id}")
        if status.get("status") == "completed":
            return _request("GET", f"{RESEARCH_API}/v1/research/result/{job_id}")
        elif status.get("status") == "failed":
            return {"error": status.get("error", "Research failed")}
        time.sleep(5)
    return {"error": f"Research timed out after {max_wait}s"}

# ─── MCP Server ──────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="API for Chads",
    instructions=(
        "Agent services platform at apiforchads.com. "
        "Provides real-time crypto prices, prediction market data, "
        "deep web research, and JS-rendered web scraping. "
        "All services available via x402 micropayments on Solana."
    ),
    host="0.0.0.0",
    port=8103,
)

# ─── Price Tools ─────────────────────────────────────────────────────────────

@mcp.tool()
def get_crypto_price(asset: str) -> str:
    """Get real-time crypto price from Chainlink oracles + Binance.

    Args:
        asset: Crypto asset symbol (e.g. BTC, ETH, SOL, MATIC)

    Returns:
        JSON with price, sources, and timestamp.
    """
    result = _request("GET", f"{PRICE_API}/v1/prices/{asset.upper()}")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_prediction_market(slug: str) -> str:
    """Get Polymarket CLOB best bid/ask for a prediction market.

    Args:
        slug: Polymarket market slug (e.g. 'will-bitcoin-hit-100k-in-2026')

    Returns:
        JSON with best bid, best ask, spread, and market info.
    """
    result = _request("GET", f"{PRICE_API}/v1/clob/{slug}")
    return json.dumps(result, indent=2)

# ─── Research Tools ──────────────────────────────────────────────────────────

@mcp.tool()
def quick_research(query: str) -> str:
    """Run a quick web-grounded research query (~20 seconds).
    Uses Gemini Flash with Google Search for fast, cited answers.

    Args:
        query: Research question or topic (5-2000 chars)

    Returns:
        Research report with sources (400-600 words).
    """
    result = _request("POST", f"{RESEARCH_API}/v1/research", {
        "query": query,
        "tier": "quick"
    })

    if "job_id" in result:
        return json.dumps(_poll_research(result["job_id"], max_wait=60), indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def deep_research(query: str) -> str:
    """Run a deep research investigation (~5 minutes).
    Uses Gemini Deep Research Pro for comprehensive, multi-source cited reports.

    Args:
        query: Research question or topic (5-2000 chars)

    Returns:
        Comprehensive research report with citations.
    """
    result = _request("POST", f"{RESEARCH_API}/v1/research", {
        "query": query,
        "tier": "deep"
    })

    if "job_id" in result:
        return json.dumps(_poll_research(result["job_id"], max_wait=420), indent=2)
    return json.dumps(result, indent=2)

# ─── Render Tools ────────────────────────────────────────────────────────────

@mcp.tool()
def render_webpage(url: str, format: str = "markdown", max_chars: int = 50000) -> str:
    """Render a web page with headless Chromium and extract content.
    Handles JavaScript-rendered pages that simple fetchers can't read.

    Args:
        url: Full URL to render (https:// required)
        format: Output format — 'markdown', 'text', or 'html'
        max_chars: Maximum characters to return (100-200000)

    Returns:
        JSON with title, content, links, and render time.
    """
    result = _request("POST", f"{RENDER_API}/v1/render", {
        "url": url,
        "format": format,
        "max_chars": max_chars,
        "block_images": True,
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def screenshot_webpage(url: str, full_page: bool = True) -> str:
    """Capture a screenshot of a web page as PNG (base64 encoded).

    Args:
        url: Full URL to screenshot (https:// required)
        full_page: True for full page, False for viewport only

    Returns:
        JSON with base64-encoded PNG screenshot and metadata.
    """
    result = _request("POST", f"{RENDER_API}/v1/render/screenshot", {
        "url": url,
        "full_page": full_page,
    })
    # Truncate base64 in display but keep it in response
    if "screenshot_base64" in result:
        preview = result.copy()
        preview["screenshot_base64"] = preview["screenshot_base64"][:100] + "...[truncated]"
        preview["note"] = "Full base64 data available in the screenshot_base64 field"
        return json.dumps(preview, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def extract_from_webpage(url: str, selector: str, format: str = "text") -> str:
    """Extract specific elements from a web page using CSS selectors.

    Args:
        url: Full URL to render (https:// required)
        selector: CSS selector (e.g. 'h1', '.article-body', '#main-content')
        format: Output format — 'text', 'markdown', or 'html'

    Returns:
        JSON with matched elements, count, and content.
    """
    result = _request("POST", f"{RENDER_API}/v1/render/extract", {
        "url": url,
        "selector": selector,
        "format": format,
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def webpage_to_pdf(url: str) -> str:
    """Convert a web page to PDF document (base64 encoded).

    Args:
        url: Full URL to convert (https:// required)

    Returns:
        JSON with base64-encoded PDF and metadata.
    """
    result = _request("POST", f"{RENDER_API}/v1/render/pdf", {
        "url": url,
    })
    if "pdf_base64" in result:
        preview = result.copy()
        preview["pdf_base64"] = preview["pdf_base64"][:100] + "...[truncated]"
        preview["note"] = "Full base64 data available in the pdf_base64 field"
        return json.dumps(preview, indent=2)
    return json.dumps(result, indent=2)

# ─── Catalog Tool ────────────────────────────────────────────────────────────

@mcp.tool()
def list_services() -> str:
    """List all available API for Chads services with pricing.

    Returns:
        Complete service catalog with endpoints, descriptions, and x402 pricing.
    """
    catalog = {
        "platform": "API for Chads",
        "website": "https://apiforchads.com",
        "payment": {
            "protocol": "x402",
            "network": "solana",
            "recipient": "EDQQe7Nufgvo2A6uXTmCpTr2FumZRB3fNzTH4Wuvpvpd",
        },
        "services": {
            "price": {
                "base_url": "https://price.apiforchads.com",
                "endpoints": {
                    "/v1/prices/{asset}": {"price": "0.0001 SOL", "desc": "Crypto price (Chainlink + Binance)"},
                    "/v1/clob/{slug}": {"price": "0.0001 SOL", "desc": "Polymarket CLOB orderbook"},
                },
            },
            "research": {
                "base_url": "https://research.apiforchads.com",
                "endpoints": {
                    "/v1/research (quick)": {"price": "0.005 SOL", "desc": "Web-grounded research, ~20s"},
                    "/v1/research (deep)": {"price": "0.02 SOL", "desc": "Full cited report, ~5min"},
                },
            },
            "render": {
                "base_url": "https://render.apiforchads.com",
                "endpoints": {
                    "/v1/render": {"price": "0.0003 SOL", "desc": "Page → markdown/text/html"},
                    "/v1/render/screenshot": {"price": "0.0005 SOL", "desc": "Full-page PNG screenshot"},
                    "/v1/render/extract": {"price": "0.0003 SOL", "desc": "CSS selector extraction"},
                    "/v1/render/pdf": {"price": "0.0005 SOL", "desc": "Page → PDF"},
                },
            },
        },
    }
    return json.dumps(catalog, indent=2)

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="API for Chads MCP Server")
    parser.add_argument("--http", action="store_true", help="Run as Streamable HTTP server")
    parser.add_argument("--port", type=int, default=8103, help="HTTP port (default: 8103)")
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
