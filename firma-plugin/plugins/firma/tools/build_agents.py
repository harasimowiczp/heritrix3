#!/usr/bin/env python3
"""Generuje agents/*.md oraz skills/roles/catalog/roles-index.md z catalog/roles.json.

Użycie:
  python3 tools/build_agents.py                 # modele zgodnie z katalogiem
  python3 tools/build_agents.py --model inherit # wszystkie role na modelu sesji
  python3 tools/build_agents.py --only "Inżynieria,Kontrola,prawnik"  # tylko wybrane działy/role
                                                # (mniej agentów = mniej tokenów w każdej sesji)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- wygenerowano: tools/build_agents.py (źródło: catalog/roles.json) -->"

TOOLS = {
    "rw": "Read, Grep, Glob, Edit, Write, Bash, Skill",
    "doc": "Read, Grep, Glob, Edit, Write, Skill",
    "ro": "Read, Grep, Glob",
}
MODE_RULE = {
    "rw": "Możesz edytować pliki i uruchamiać lokalne polecenia (build, testy, skanery offline).",
    "doc": "Możesz tworzyć i edytować dokumenty; nie uruchamiasz poleceń powłoki.",
    "ro": "Tylko odczyt: nie modyfikujesz żadnych plików.",
}

BODY = """{marker}
Jesteś: **{name}** w wirtualnej firmie (dział: {dept}).

- Zakres: {does}
- Rezultaty: {out}
- Preferowane skille (jeśli zainstalowane): {skills}
- Narzędzia offline: {cli}
- Lokalne MCP: {mcp}
- Pogłębione procesy: `$FIRMA_BABYSITTER_LIB/{bs}` (lokalny klon biblioteki babysitter, jeśli ustawiony)
- Uprawnienia: {mode_rule}

## Zasady poufności (bezwzględne)
- Pracujesz wyłącznie na lokalnych plikach. Nie używasz internetu, zewnętrznych API ani chmurowych konektorów.
- Nie uruchamiasz poleceń sieciowych (curl, wget, ssh, scp, rsync, git push/pull/fetch/clone, instalacje pakietów, publish). Jeśli zadanie tego wymaga — przerwij i zgłoś to w raporcie.
- Sekrety i dane osobowe cytujesz tylko w niezbędnym minimum; odwołuj się przez `plik:linia`.

## Zasady pracy
- Zacznij od kryteriów akceptacji ze zlecenia; jeśli ich brak — przyjmij rozsądne i wypisz je.
- Pracuj partiami (ok. 5 plików lub 1 sekcja naraz) i sprawdzaj wynik po każdej partii.
- Oszczędzaj tokeny: czytaj fragmenty (Grep, zakresy linii), nie całe katalogi; nie powtarzaj treści zlecenia.
- Nie zgaduj faktów — oznaczaj niepewność.

## Raport końcowy (maks. ok. 200 słów)
1. Wynik — co zrobiono, ścieżki plików
2. Weryfikacja — jak sprawdzono
3. Ryzyka i otwarte kwestie
4. Następny krok / rola, która powinna przejąć
"""


def join(items):
    return ", ".join(items) if items else "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="nadpisz model wszystkich ról (np. inherit)")
    ap.add_argument("--only", help="lista działów lub id ról rozdzielona przecinkami")
    args = ap.parse_args()

    roles = json.loads((ROOT / "catalog/roles.json").read_text(encoding="utf-8"))["roles"]
    if args.only:
        keep = {x.strip() for x in args.only.split(",") if x.strip()}
        roles = [r for r in roles if r["id"] in keep or r["dept"] in keep]
        roles += [r for r in json.loads((ROOT / "catalog/roles.json").read_text(encoding="utf-8"))["roles"]
                  if r["id"] in ("kontroler-jakosci", "oficer-poufnosci") and r not in roles]
    agents_dir = ROOT / "agents"
    agents_dir.mkdir(exist_ok=True)

    ids = set()
    index = [
        "# Katalog ról firmy (indeks)",
        "",
        "Format: `id` [dział · model · uprawnienia] — kiedy angażować | preferowane skille",
        "",
    ]
    dept = None
    for r in roles:
        ids.add(r["id"])
        model = args.model or r["model"]
        desc = f'{r["name"]}: {r["when"]}'
        front = (
            f'---\nname: {r["id"]}\ndescription: {json.dumps(desc, ensure_ascii=False)}\n'
            f'tools: {TOOLS[r["mode"]]}\nmodel: {model}\n---\n'
        )
        body = BODY.format(
            marker=MARKER, name=r["name"], dept=r["dept"], does=r["does"], out=r["out"],
            skills=join(r["skills"]), cli=join(r["cli"]), mcp=join(r["mcp"]),
            bs=r["bs"], mode_rule=MODE_RULE[r["mode"]],
        )
        (agents_dir / f'{r["id"]}.md').write_text(front + body, encoding="utf-8")

        if r["dept"] != dept:
            dept = r["dept"]
            index.append(f"\n## {dept}")
        index.append(
            f'- `{r["id"]}` [{model} · {r["mode"]}] — {r["when"]} | {join(r["skills"])}'
        )

    # usuń agentów wygenerowanych wcześniej, których nie ma już w katalogu
    for f in agents_dir.glob("*.md"):
        if f.stem not in ids and MARKER in f.read_text(encoding="utf-8"):
            f.unlink()

    out = ROOT / "skills/roles/catalog/roles-index.md"
    out.write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Wygenerowano {len(roles)} agentów oraz {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
