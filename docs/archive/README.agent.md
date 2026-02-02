# 🤖 AGENT INSTRUCTIONS - READ BEFORE DOING ANYTHING

This file contains **mandatory instructions** for AI agents working with the KenPom MCP server.

---

## 🚫 DO NOT MODIFY THIS CODEBASE

The KenPom MCP server is **production-ready and tested**. If an MCP tool returns an error:

1. **The code is NOT broken** - check your parameters instead
2. **Do NOT edit** any files in `src/kenpom_mcp/`
3. **Do NOT create** any `.py` scripts in the project root
4. **Do NOT run** `grep` on `.env` files or print credentials

---

## ✅ CORRECT PARAMETER FORMATS

| Tool               | Parameter | Format  | Example                    |
| ------------------ | --------- | ------- | -------------------------- |
| All                | `season`  | String  | `"2026"` not `2026`        |
| `get_fanmatch`     | `date`    | String  | `"2025-12-23"`             |
| `get_team_stats`   | `defense` | Boolean | `true` or `false`          |
| `get_player_stats` | `metric`  | String  | `"eFG"`, `"ORtg"`, `"Min"` |

---

## ⚠️ COMMON ERRORS AND SOLUTIONS

| Error                   | Cause                | Solution                             |
| ----------------------- | -------------------- | ------------------------------------ |
| `KENPOM_EMAIL required` | Stale server process | **User must restart VS Code**        |
| Empty result `[]`       | Invalid season/date  | Check if data exists for that period |
| `302 Found` redirect    | Session expired      | Retry the request once               |

---

## 🛑 IF YOU ARE TEMPTED TO "FIX" SOMETHING

**STOP. ASK THE USER FIRST.**

The correct response to MCP errors is almost always:

> "Please restart VS Code to reload the MCP server."

NOT:

> "Let me check server.py to debug this..."

---

_This notice is for AI agents. Humans can ignore it._
