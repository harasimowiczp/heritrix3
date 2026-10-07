#!/usr/bin/env python3
"""Lokalna inwentaryzacja narzędzi Claude Code z oceną poufności. Działa offline, tylko stdlib.

Czyta wyłącznie lokalne pliki konfiguracyjne (~/.claude, projekt) i nic nie wysyła.

Użycie:
  inventory.py --audit                          # stan prywatności, MCP, pluginy
  inventory.py --match "umowa,contract,legal"   # + pasujące skille i agenci
  inventory.py --bs "contract,gdpr"             # + top procesy/agenci/skille z biblioteki babysitter
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

HOME = Path.home()
CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", HOME / ".claude"))
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
CACHE = CLAUDE_DIR / "firma-cache"

CLOUD_HINTS = re.compile(
    r"github|gitlab|slack|notion|gmail|google|gdrive|drive|calendar|aws|azure|gcp|stripe|hubspot|"
    r"salesforce|jira|atlassian|linear|figma|brave|tavily|exa|firecrawl|perplexity|openai|"
    r"search|fetch|browser|puppeteer|playwright|scrape|brightdata|zapier|airtable|supabase|"
    r"vercel|cloudflare|sentry|datadog|asana|monday|trello|dropbox|box|twilio|sendgrid",
    re.I,
)
NET_IN_SKILL = re.compile(r"WebFetch|WebSearch|https?://(?!localhost|127\.0\.0\.1)|\bcurl\b|\bwget\b|mcp__", re.I)
SECRET_ENV = re.compile(r"KEY|TOKEN|SECRET|PASSWORD", re.I)
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def load_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def frontmatter(path):
    """Prosty parser frontmattera YAML (klucze jednoliniowe i bloki > / |)."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}, ""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        lines = text[3:end].splitlines() if end > 0 else []
        key = None
        for ln in lines:
            m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", ln)
            if m:
                key, val = m.group(1), m.group(2).strip()
                meta[key] = "" if val in (">", "|", ">-", "|-") else val.strip("\"'")
            elif key and ln.startswith((" ", "\t")) and key in meta:
                meta[key] = (meta[key] + " " + ln.strip()).strip()
    return meta, text


def short(s, n=100):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ---------- pluginy ----------
def plugin_dirs():
    found = {}
    data = load_json(CLAUDE_DIR / "plugins/installed_plugins.json").get("plugins", {})
    for pid, entries in data.items():
        for e in entries if isinstance(entries, list) else [entries]:
            ip = e.get("installPath") if isinstance(e, dict) else None
            if ip and Path(ip).is_dir():
                found[str(Path(ip).resolve())] = pid
    root = CLAUDE_DIR / "plugins"
    if root.is_dir():
        for manifest in root.glob("**/.claude-plugin/plugin.json"):
            if "marketplaces" in manifest.parts:
                continue
            d = manifest.parent.parent.resolve()
            found.setdefault(str(d), load_json(manifest).get("name", d.name))
    return found


def enabled_map():
    res = {}
    for p in (CLAUDE_DIR / "settings.json", PROJECT / ".claude/settings.json", PROJECT / ".claude/settings.local.json"):
        res.update(load_json(p).get("enabledPlugins", {}) or {})
    return res


# ---------- MCP ----------
def classify_mcp(cfg):
    if "url" in cfg or cfg.get("type") in ("http", "sse", "ws"):
        host = (urlparse(cfg.get("url") or "").hostname or "").lower()
        if host in LOCAL_HOSTS:
            return "LOKALNY", f"{cfg.get('type', 'http')} na {host}"
        return "ZEWNĘTRZNY", host or "konektor chmurowy (adres nadawany przez claude.ai)"
    cmd = " ".join([str(cfg.get("command", ""))] + [str(a) for a in cfg.get("args", [])])
    external = []
    if CLOUD_HINTS.search(cmd):
        external.append("proces lokalny, ale łączy się z usługą chmurową")
    if any(SECRET_ENV.search(k) for k in (cfg.get("env") or {})):
        external.append("wymaga klucza API usługi zewnętrznej")
    if external:
        return "ZEWNĘTRZNY", "; ".join(external)
    if re.search(r"\b(npx|uvx|pipx|bunx|dlx)\b", cmd):
        return "UWAGA", "pobiera pakiet z sieci przy starcie — zainstaluj lokalnie i przypnij wersję"
    return "LOKALNY", f"stdio: {short(cmd, 60)} (zweryfikuj kod serwera)"


def mcp_servers(plugins):
    out = []
    cj = load_json(HOME / ".claude.json") or load_json(CLAUDE_DIR / ".claude.json")
    for n, c in (cj.get("mcpServers") or {}).items():
        out.append((n, "użytkownik", c))
    proj = (cj.get("projects") or {}).get(str(PROJECT), {})
    for n, c in (proj.get("mcpServers") or {}).items():
        out.append((n, "projekt (lokalny)", c))
    for n, c in (load_json(PROJECT / ".mcp.json").get("mcpServers") or {}).items():
        out.append((n, "projekt (.mcp.json)", c))
    for d, pid in plugins.items():
        cfg = load_json(Path(d) / ".mcp.json")
        servers = cfg.get("mcpServers", cfg) if isinstance(cfg, dict) else {}
        man = load_json(Path(d) / ".claude-plugin/plugin.json").get("mcpServers")
        if isinstance(man, dict):
            servers = {**servers, **man}
        for n, c in servers.items():
            if isinstance(c, dict):
                out.append((n, f"plugin {pid}", c))
    return out


# ---------- skille i agenci ----------
def collect(plugins):
    skills, agents = [], []
    roots = [("użytkownik", CLAUDE_DIR), ("projekt", PROJECT / ".claude")]
    roots += [(f"plugin {pid}", Path(d)) for d, pid in plugins.items()]
    for src, base in roots:
        for f in list(base.glob("skills/*/SKILL.md")) + list(base.glob("commands/*.md")):
            meta, text = frontmatter(f)
            name = meta.get("name") or (f.parent.name if f.name == "SKILL.md" else f.stem)
            net = bool(NET_IN_SKILL.search(text)) or "WebFetch" in meta.get("allowed-tools", "")
            skills.append((name, src, meta.get("description", ""), net))
        for f in base.glob("agents/*.md"):
            meta, _ = frontmatter(f)
            tools = meta.get("tools", "")
            risk = "dziedziczy wszystkie narzędzia (także MCP/sieć)" if not tools else (
                "ma WebFetch/WebSearch" if re.search(r"WebFetch|WebSearch|\*", tools) else "")
            agents.append((meta.get("name", f.stem), src, meta.get("description", ""), risk))
    return skills, agents


def matches(text, kws):
    t = text.lower()
    return sum(1 for k in kws if k in t)


# ---------- prywatność ----------
def privacy_status():
    env = {}
    for p in (CLAUDE_DIR / "settings.json", PROJECT / ".claude/settings.json", PROJECT / ".claude/settings.local.json"):
        env.update(load_json(p).get("env", {}) or {})
    env = {**env, **{k: v for k, v in os.environ.items()}}
    settings = [load_json(p) for p in (CLAUDE_DIR / "settings.json", PROJECT / ".claude/settings.json",
                                       PROJECT / ".claude/settings.local.json")]
    deny = " ".join(" ".join(s.get("permissions", {}).get("deny", []) or []) for s in settings)
    sandbox = any((s.get("sandbox") or {}).get("enabled") for s in settings)

    if env.get("CLAUDE_CODE_USE_BEDROCK") == "1":
        model = f"Amazon Bedrock (region {env.get('AWS_REGION', '?')}) — dane w Twoim koncie AWS"
    elif env.get("CLAUDE_CODE_USE_VERTEX") == "1":
        model = f"Google Vertex AI (region {env.get('CLOUD_ML_REGION', '?')}) — dane w Twoim projekcie GCP"
    elif env.get("ANTHROPIC_BASE_URL"):
        host = (urlparse(env["ANTHROPIC_BASE_URL"]).hostname or "").lower()
        if host in LOCAL_HOSTS:
            model = f"lokalny endpoint {host} — inferencja na tej maszynie"
        elif host.endswith("anthropic.com"):
            model = "Anthropic API (chmura) — treść promptów i czytanych plików trafia do dostawcy modelu"
        else:
            model = f"endpoint {host} — ZEWNĘTRZNY (sprawdź, kto go obsługuje)"
    else:
        model = "Anthropic API (chmura) — treść promptów i czytanych plików trafia do dostawcy modelu"

    tele = env.get("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC") == "1" or (
        env.get("DISABLE_TELEMETRY") == "1" and env.get("DISABLE_ERROR_REPORTING") == "1")
    gi = PROJECT / ".gitignore"
    gitignored = gi.exists() and ".firma" in gi.read_text(encoding="utf-8", errors="replace")
    rows = [
        ("Inferencja modelu", model, None),
        ("Telemetria/raporty błędów", "wyłączone" if tele else "WŁĄCZONE", tele),
        ("Konektory claude.ai", "wyłączone" if env.get("ENABLE_CLAUDEAI_MCP_SERVERS") == "false" else "mogą być aktywne",
         env.get("ENABLE_CLAUDEAI_MCP_SERVERS") == "false"),
        ("WebFetch/WebSearch w deny", "tak" if ("WebFetch" in deny and "WebSearch" in deny) else "NIE",
         "WebFetch" in deny and "WebSearch" in deny),
        ("Sandbox Bash (izolacja sieci)", "włączony" if sandbox else "wyłączony", sandbox),
        ("Strażnik firmy FIRMA_PRIVACY", env.get("FIRMA_PRIVACY", "strict (domyślnie)"), env.get("FIRMA_PRIVACY", "strict") != "off"),
        (".firma/ w .gitignore projektu", "tak" if gitignored else "nie", gitignored),
    ]
    return rows


# ---------- babysitter ----------
def babysitter_index(lib, reindex):
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / "babysitter-index.json"
    if cache.exists() and not reindex:
        data = load_json(cache)
        if data.get("lib") == str(lib):
            return data["items"]
    items = []
    spec = lib / "specializations"
    for f in spec.glob("**/agents/*/AGENT.md"):
        m, _ = frontmatter(f)
        items.append(["agent", m.get("name", f.parent.name), short(m.get("description"), 140), str(f.relative_to(lib))])
    for f in spec.glob("**/skills/*/SKILL.md"):
        m, _ = frontmatter(f)
        items.append(["skill", m.get("name", f.parent.name), short(m.get("description"), 140), str(f.relative_to(lib))])
    for f in list(spec.glob("**/*.js")) + list((lib / "methodologies").glob("**/*.js")):
        if "__tests__" in f.parts or "node_modules" in f.parts:
            continue
        head = f.read_text(encoding="utf-8", errors="replace")[:1200]
        m = re.search(r"@description\s+(.+?)(?:\n\s*\*\s*@|\*/)", head, re.S)
        if m:
            desc = re.sub(r"\s*\*\s*", " ", m.group(1))
            items.append(["proces", f.stem, short(desc, 140), str(f.relative_to(lib))])
    cache.write_text(json.dumps({"lib": str(lib), "items": items}), encoding="utf-8")
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", default="", help="słowa kluczowe rozdzielone przecinkami")
    ap.add_argument("--bs", default="", help="słowa kluczowe (EN) do biblioteki babysitter")
    ap.add_argument("--audit", action="store_true", help="tylko prywatność, MCP i pluginy")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--reindex", action="store_true")
    a = ap.parse_args()

    plugins = plugin_dirs()
    enabled = enabled_map()
    print("## Stan prywatności")
    for k, v, ok in privacy_status():
        mark = "" if ok is None else (" ✅" if ok else " ⚠️")
        print(f"- {k}: {v}{mark}")

    servers = mcp_servers(plugins)
    groups = {}
    for name, src, cfg in servers:
        cls, why = classify_mcp(cfg)
        groups.setdefault((cls, name, why), []).append(src)
    print(f"\n## Serwery MCP ({len(groups)} unikalnych)")
    order = {"ZEWNĘTRZNY": 0, "UWAGA": 1, "LOKALNY": 2}
    ext = sorted({name for (cls, name, _), _s in groups.items() if cls == "ZEWNĘTRZNY"})
    for (cls, name, why), srcs in sorted(groups.items(), key=lambda x: (order[x[0][0]], x[0][1])):
        if cls == "ZEWNĘTRZNY" and not a.audit:
            continue
        where = srcs[0] if len(srcs) == 1 else f"źródła: {len(srcs)}"
        print(f"- `{name}` [{where}] — **{cls}**: {why}")
    if ext and not a.audit:
        names = ", ".join(ext[:30]) + (f" … (+{len(ext) - 30})" if len(ext) > 30 else "")
        print(f"- **ZEWNĘTRZNE ({len(ext)})** — nie używać w trybie poufnym: {names}")
    if not servers:
        print("- brak w plikach konfiguracyjnych")
    print("- Uwaga: konektory claude.ai (np. Gmail, Notion, Drive) nie są widoczne w plikach — zawsze ZEWNĘTRZNE.")

    print(f"\n## Pluginy ({len(plugins)})")
    names = []
    for d, pid in sorted(plugins.items(), key=lambda x: x[1]):
        state = enabled.get(pid)
        names.append(pid + ("" if state is None else (" (wł.)" if state else " (wył.)")))
    print("- " + ", ".join(names) if names else "- brak")

    if a.audit and not a.match and not a.bs:
        return
    skills, agents = collect(plugins)
    kws = [k.strip().lower() for k in a.match.split(",") if k.strip()]
    for label, rows, flag in (("Skille i komendy", skills, "⚠ sieć"), ("Agenci", agents, None)):
        if kws:
            scored = sorted(((matches(r[0] + " " + r[2], kws), r) for r in rows), key=lambda x: -x[0])
            hit = [r for s, r in scored if s > 0][: a.limit]
            print(f"\n## {label} — pasujące do: {', '.join(kws)} ({len(hit)} z {len(rows)})")
            for r in hit:
                warn = (f" ⚠ {r[3]}" if isinstance(r[3], str) and r[3] else (f" {flag}" if r[3] is True else ""))
                print(f"- `{r[0]}` [{r[1]}] — {short(r[2])}{warn}")
        else:
            print(f"\n## {label}: {len(rows)} (podaj --match, aby zobaczyć opisy)")

    if a.bs:
        lib = os.environ.get("FIRMA_BABYSITTER_LIB")
        if not lib or not (Path(lib) / "specializations").is_dir():
            print("\n## Babysitter: ustaw FIRMA_BABYSITTER_LIB=<klon>/library, aby przeszukiwać bibliotekę offline")
            return
        items = babysitter_index(Path(lib), a.reindex)
        bk = [k.strip().lower() for k in a.bs.split(",") if k.strip()]
        scored = sorted(((matches(i[1], bk) * 3 + matches(i[2], bk), i) for i in items), key=lambda x: -x[0])
        hit = [i for s, i in scored if s > 0][: a.limit]
        print(f"\n## Babysitter library ({len(hit)} z {len(items)}) — {', '.join(bk)}")
        for kind, name, desc, rel in hit:
            print(f"- {kind} `{name}` — {desc} ({rel})")


if __name__ == "__main__":
    sys.exit(main())
