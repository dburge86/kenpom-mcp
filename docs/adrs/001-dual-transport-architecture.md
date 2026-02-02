# ADR 001: Dual Transport Architecture (STDIO + HTTP/SSE)

**Status:** Accepted
**Date:** January 2026 (pre-polish)
**Decision Maker:** David Burgess

---

## Context

The KenPom MCP server needs to support two distinct use cases:

1. **Local Development & Desktop Use:** Users running Claude Desktop or other MCP clients locally
2. **Remote/Cloud Deployment:** Global access via Google Cloud Run for remote clients

The Model Context Protocol (MCP) specification supports multiple transport mechanisms, but choosing the right one(s) requires understanding the trade-offs.

---

## Decision

Implement **dual transport architecture** with:

1. **STDIO Transport** (via FastMCP framework)
   - For local MCP clients like Claude Desktop
   - Process-based communication via stdin/stdout
   - Simple, low-latency, no network overhead

2. **HTTP/SSE Transport** (via Starlette framework)
   - For remote clients and Cloud Run deployment
   - RESTful endpoints + Server-Sent Events for streaming
   - Supports API key authentication
   - Globally accessible URL

Both transports expose the same 13 data tools via a unified tool registry (`tools.py`).

---

## Consequences

### Positive

✅ **Flexibility:** Supports both local and remote use cases
✅ **Developer Experience:** Local dev uses fast STDIO, no network latency
✅ **Global Access:** HTTP/SSE enables deployment to Cloud Run for worldwide use
✅ **Code Reuse:** Unified tool registry eliminates duplication (see ADR 002)
✅ **Production Ready:** HTTP transport supports authentication and rate limiting

### Negative

⚠️ **Maintenance Overhead:** Two servers to maintain (`server.py` and `http_server.py`)
⚠️ **Testing Complexity:** Each transport needs its own test strategy
⚠️ **Deployment Complexity:** Two different deployment processes (local vs Cloud Run)

### Mitigations

- **Unified Tool Registry:** Eliminates code duplication (see ADR 002)
- **Shared Scraper:** Both transports use the same `KenPomScraper` class
- **Shared Parsers:** All HTML parsing logic is in `parsers/` module
- **Result:** Only transport-specific code differs (~100 lines per transport)

---

## Alternatives Considered

### 1. STDIO Only
**Pros:** Simplest implementation, no network code
**Cons:** No remote access, can't deploy to Cloud Run
**Rejected:** Doesn't meet remote use case requirement

### 2. HTTP/SSE Only
**Pros:** Single transport, universally accessible
**Cons:** Local clients must connect via network (slower, requires auth)
**Rejected:** Poor local developer experience

### 3. WebSocket Transport
**Pros:** Full-duplex communication, widely supported
**Cons:** More complex than SSE, FastMCP doesn't natively support it
**Rejected:** SSE is sufficient for MCP streaming, simpler to implement

---

## Implementation Details

### STDIO Transport (server.py)
```python
# FastMCP framework
from mcp import FastMCP

mcp = FastMCP("kenpom-mcp")

@mcp.tool()
async def get_ratings(season: str = "2026") -> list[dict]:
    return await call_tool_handler("get_ratings", {"season": season})
```

### HTTP/SSE Transport (http_server.py)
```python
# Starlette framework
from starlette.applications import Starlette
from starlette.routing import Route

async def mcp_endpoint(request):
    data = await request.json()
    result = await call_tool_handler(data["method"], data["params"])
    return JSONResponse({"result": result})

app = Starlette(routes=[
    Route("/mcp", mcp_endpoint, methods=["POST"]),
    Route("/sse", sse_endpoint),
])
```

---

## Related Decisions

- **ADR 002:** Unified Tool Registry Pattern (eliminates duplication between transports)

---

## References

- [MCP Specification - Transports](https://modelcontextprotocol.io/docs/concepts/transports)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)

---

**Last Updated:** 2026-02-02
