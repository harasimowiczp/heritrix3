#!/usr/bin/env python3
"""SessionStart: krótka informacja o trybie poufnym (oszczędnie z tokenami — 1-2 zdania)."""
import json
import os
import sys

mode = os.environ.get("FIRMA_PRIVACY", "strict").lower()
if mode == "off":
    sys.exit(0)
msg = (f"Firma: tryb poufny '{mode}'. Pracuj tylko lokalnie — bez WebFetch/WebSearch, zewnętrznych MCP "
       "i poleceń sieciowych. Dobór zespołu i narzędzi: /firma:roles.")
if os.environ.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC") != "1":
    msg += " Uwaga: telemetria nie jest wyłączona — zaproponuj użytkownikowi /firma:roles-audyt."
json.dump({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}},
          sys.stdout, ensure_ascii=False)
