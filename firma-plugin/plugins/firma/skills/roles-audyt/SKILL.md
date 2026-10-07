---
name: roles-audyt
description: Audyt poufności lokalnej instalacji Claude Code — co może wysłać dane na zewnątrz (model, telemetria, MCP, konektory, pluginy) i jak to zamknąć. Użyj przy /firma:roles-audyt lub pytaniu o prywatność konfiguracji.
allowed-tools: Read, Bash(python3:*)
---

# Audyt poufności

1. Uruchom `python3 "${CLAUDE_SKILL_DIR}/../roles/scripts/inventory.py" --audit`.
2. Przedstaw wynik w trzech częściach (maks. 25 linii):
   - **Co wychodzi na zewnątrz teraz** — inferencja modelu, telemetria, każdy serwer ZEWNĘTRZNY/UWAGA.
   - **Poprawki** — konkretne wpisy do `~/.claude/settings.json` na podstawie
     `${CLAUDE_SKILL_DIR}/../../templates/settings.private.json` (pokaż tylko brakujące klucze),
     wyłączenie pluginów ze zdalnymi konektorami (`claude plugin disable <nazwa>`), `.firma/` w `.gitignore`.
   - **Ryzyko rezydualne** — dopóki model działa w chmurze (Anthropic API, Bedrock, Vertex), treść promptów
     i czytanych plików trafia do dostawcy modelu. Pełna lokalność = lokalny model (patrz README, sekcja „Poziomy poufności”).
3. Niczego nie zmieniaj w konfiguracji bez wyraźnej zgody użytkownika.
