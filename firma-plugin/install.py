#!/usr/bin/env python3
"""Instalator lokalny wtyczki „firma”. Działa offline, nic nie wysyła.

  python3 install.py              # skrót /roles (~/.claude/commands/roles.md) + instrukcje
  python3 install.py --settings   # dodatkowo scala ustawienia prywatności z ~/.claude/settings.json (z kopią .bak)
  python3 install.py --babysitter /sciezka/babysitter/library   # zapisuje FIRMA_BABYSITTER_LIB w ustawieniach
"""
import argparse
import json
import os
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE / "plugins/firma"
CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))


def backup(p):
    if p.exists():
        b = p.with_name(p.name + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(p, b)
        print(f"  kopia: {b}")


def install_alias():
    dst = CLAUDE_DIR / "commands/roles.md"
    src = PLUGIN / "templates/roles-alias.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"):
        print(f"= skrót /roles już zainstalowany ({dst})")
        return
    backup(dst)
    shutil.copy2(src, dst)
    print(f"+ skrót /roles → {dst}")


def merge_settings(extra_env):
    path = CLAUDE_DIR / "settings.json"
    cur = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    tpl = json.loads((PLUGIN / "templates/settings.private.json").read_text(encoding="utf-8"))
    tpl["env"].update(extra_env)
    env = cur.setdefault("env", {})
    for k, v in tpl["env"].items():
        if k.startswith("FIRMA_") and k in env and k not in extra_env:
            continue  # nie nadpisuj wcześniejszych wyborów użytkownika (tryb, lista MCP)
        env[k] = v
    deny = cur.setdefault("permissions", {}).setdefault("deny", [])
    deny += [d for d in tpl["permissions"]["deny"] if d not in deny]
    cur.setdefault("sandbox", tpl["sandbox"])
    cur.setdefault("cleanupPeriodDays", tpl["cleanupPeriodDays"])
    cur.setdefault("disableClaudeAiConnectors", tpl["disableClaudeAiConnectors"])
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"+ ustawienia prywatności scalone → {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", action="store_true")
    ap.add_argument("--babysitter", help="ścieżka do katalogu library/ z lokalnego klonu babysitter")
    a = ap.parse_args()

    install_alias()
    extra = {}
    if a.babysitter:
        lib = Path(a.babysitter).expanduser().resolve()
        if not (lib / "specializations").is_dir():
            raise SystemExit(f"! {lib} nie wygląda na babysitter/library (brak specializations/)")
        extra["FIRMA_BABYSITTER_LIB"] = str(lib)
    if a.settings or extra:
        merge_settings(extra)

    print(f"""
Dalej (jednorazowo, wszystko z dysku lokalnego):
  claude plugin marketplace add "{HERE}"
  claude plugin install firma@firma-lokalna
Potem w Claude Code: /roles <zadanie>   (lub /firma:roles), audyt: /firma:roles-audyt""")


if __name__ == "__main__":
    main()
