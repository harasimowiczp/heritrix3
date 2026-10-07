#!/usr/bin/env python3
"""Strażnik poufności (hook PreToolUse). Blokuje lub wstrzymuje do akceptacji wywołania,
które mogą wysłać dane poza komputer: WebFetch/WebSearch, zewnętrzne MCP, polecenia sieciowe w Bash.

Tryb: zmienna FIRMA_PRIVACY = strict (domyślnie) | warn | off
  strict — eksfiltracja: deny; pobieranie (instalacje, git pull): ask
  warn   — wszystko podejrzane: ask
Dozwolone serwery MCP: FIRMA_ALLOW_MCP="sqlite,filesystem" (nazwy lokalnych serwerów).

To zabezpieczenie heurystyczne (wzorce poleceń). Twardą izolację sieci zapewnia sandbox
Claude Code (sandbox.enabled + sandbox.network.allowedDomains) — patrz README.
"""
import json
import os
import re
import sys

EXFIL = [
    (r"\b(curl|wget|nc|ncat|netcat|socat|telnet|ftp|tftp|sftp|scp|ssh|aria2c|xh|lynx|w3m)\b", "klient sieciowy"),
    (r"\brsync\b.*(\S+:\S|rsync://)", "rsync do zdalnego hosta"),
    (r"\bgit\s+(push|send-email|request-pull)\b", "wysyłka repozytorium"),
    (r"\b(npm|pnpm|yarn|bun)\s+publish\b|\btwine\s+upload\b|\bgem\s+push\b|\bcargo\s+publish\b"
     r"|\bmvn\b.*\bdeploy\b|\bdocker\s+(push|login)\b", "publikacja pakietu/obrazu"),
    (r"\b(gh|glab|aws|gcloud|gsutil|bq|az|azcopy|heroku|vercel|netlify|firebase|flyctl|doctl|rclone|s3cmd)\s",
     "CLI usługi chmurowej"),
    (r"\b(sendmail|mutt|mailx|swaks)\b", "wysyłka e-mail"),
]
SUSPECT = [
    (r"requests\.(get|post|put|patch)|urllib\.request|http\.client|socket\.(socket|create_connection)"
     r"|Invoke-WebRequest|Invoke-RestMethod|\biwr\b|\birm\b|Net\.WebClient|Start-BitsTransfer", "kod sieciowy w skrypcie"),
    (r"https?://(?!localhost|127\.0\.0\.1|\[::1\])[\w.-]+", "adres URL zdalnego hosta"),
    (r"\b(nslookup|dig|host)\s+\S+\.\S+", "zapytanie DNS"),
    (r"\bgit\s+(pull|fetch|clone|ls-remote|submodule\s+update|remote\s+update)\b", "pobieranie z repozytorium zdalnego"),
    (r"\b(npm|pnpm|yarn|bun)\s+(i|install|add|ci|update|upgrade|dlx|x)\b|\bnpx\b|\buvx\b|\bpip3?\s+install\b"
     r"|\buv\s+(pip\s+install|add|sync)\b|\bpoetry\s+(add|install)\b|\bgem\s+install\b|\bcomposer\s+(install|require)\b"
     r"|\b(apt|apt-get|dnf|yum|brew|choco|winget|scoop)\s+install\b|\bgo\s+(get|mod\s+download)\b"
     r"|\bcargo\s+(install|fetch)\b|\bdocker\s+(pull|build)\b", "instalacja/pobieranie pakietów"),
    (r"\bmvn\b(?!.*\s(-o|--offline)\b)|\bgradlew?\b(?!.*--offline)", "build pobierający zależności (użyj -o / --offline)"),
]


def decide(tool, inp, mode, allow_mcp):
    if tool in ("WebFetch", "WebSearch"):
        return "deny" if mode == "strict" else "ask", f"{tool} wysyła zapytanie do internetu"
    if tool.startswith("mcp__"):
        server = tool.split("__")[1]
        base = re.sub(r"^plugin_[^_]+_", "", server)
        if server in allow_mcp or base in allow_mcp:
            return None, ""
        return ("deny" if mode == "strict" else "ask"), (
            f"serwer MCP '{base}' nie jest na liście lokalnych (FIRMA_ALLOW_MCP)")
    if tool == "Bash":
        cmd = inp.get("command", "")
        for pat, why in EXFIL:
            if re.search(pat, cmd, re.I):
                return ("deny" if mode == "strict" else "ask"), why
        for pat, why in SUSPECT:
            if re.search(pat, cmd, re.I):
                return "ask", why
    return None, ""


def main():
    mode = os.environ.get("FIRMA_PRIVACY", "strict").lower()
    if mode == "off":
        return 0
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    allow = {s.strip() for s in os.environ.get("FIRMA_ALLOW_MCP", "").split(",") if s.strip()} | {"ide"}
    decision, why = decide(data.get("tool_name", ""), data.get("tool_input") or {}, mode, allow)
    if decision:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"[firma/poufność:{mode}] {why}. "
                                        "Użyj alternatywy lokalnej albo zmień FIRMA_PRIVACY świadomie.",
        }}, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
