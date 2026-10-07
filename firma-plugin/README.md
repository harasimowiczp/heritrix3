# Wtyczka „firma” dla Claude Code — 47 specjalistów, `/roles`, tryb poufny

Wirtualna firma zamknięta w jednej wtyczce. Wpisujesz `/roles <zadanie>`. Agent analizuje zadanie
i proponuje minimalny zespół specjalistów oraz skille, pluginy, serwery MCP i narzędzia offline.
Do tego dostajesz plan pracy w partiach i ocenę, co mogłoby wysłać dane poza komputer.
Po Twoim „start” zadanie jest delegowane do subagentów, a całość kończy bramka jakości.

Wszystko działa lokalnie: nie ma serwera, nie ma publikacji, a instalacja odbywa się z dysku.
Przeczytaj jednak sekcję [Poziomy poufności](#poziomy-poufności), bo pewnej granicy żadna wtyczka nie przesunie.

---

## Instalacja (z dysku, offline)

Wymagania: Claude Code CLI i Python 3.8+ (hooki i skrypty używają tylko biblioteki standardowej).

```bash
cd firma-plugin
python3 install.py --settings          # skrót /roles + ustawienia prywatności (z kopią .bak)
claude plugin marketplace add "$(pwd)"
claude plugin install firma@firma-lokalna
```

Opcjonalnie możesz podpiąć bibliotekę babysitter (około 1170 agentów, 1960 skilli i 2000 procesów, przeszukiwane offline):

```bash
git clone --depth 1 https://github.com/a5c-ai/babysitter.git ~/narzedzia/babysitter   # jednorazowo
python3 install.py --babysitter ~/narzedzia/babysitter/library
```

Wersja deweloperska bez instalacji: `claude --plugin-dir ./plugins/firma`.

> **Windows:** hooki wywołują `python3`. Jeśli masz tylko `py` lub `python`, zmień polecenie
> w `plugins/firma/hooks/hooks.json`. Sandbox Bash działa na macOS, Linuksie i WSL2.

## Użycie

| Polecenie | Działanie |
|---|---|
| `/roles przygotuj umowę NDA i politykę RODO dla nowego modułu CRM` | analiza, zespół, narzędzia, plan w partiach i koszt; czeka na decyzję |
| `/roles` (bez argumentu) | bierze zadanie opisane ostatnio w czacie |
| `/roles katalog` | lista 47 ról |
| `/roles wznów` | kontynuuje plan z `.firma/plany/` (dziennik jak w babysitter) |
| `/firma:roles-audyt` | audyt: co w Twojej konfiguracji może wysłać dane na zewnątrz |

Na propozycję odpowiadasz jednym z trzech słów:
- **start**: zapis planu do `.firma/plany/…md`, delegacja partii do agentów (niezależne idą równolegle), a na końcu `kontroler-jakosci`;
- **zmień …**: poprawka propozycji;
- **zapisz**: zapis planu bez wykonania.

`/roles` to skrót instalowany przez `install.py`. Nazwa natywna to `/firma:roles`, bo komendy wtyczek mają prefiks wtyczki.

## Zespół (47 ról, 11 działów)

| Dział | Role (agenci `firma:<id>`) |
|---|---|
| Zarząd | strateg-ceo, kierownik-projektu, analityk-biznesowy, product-manager |
| Inżynieria | architekt-oprogramowania, backend-developer, frontend-developer, mobile-developer, inzynier-danych, administrator-baz-danych, devops-inzynier, inzynier-qa, specjalista-bezpieczenstwa, recenzent-kodu, inzynier-wydajnosci, specjalista-migracji, inzynier-ai, inzynier-integracji |
| Dane i analityka | analityk-danych, data-scientist, specjalista-bi |
| Projektowanie | projektant-ux, projektant-ui, specjalista-dostepnosci, ux-writer |
| Dokumentacja i treści | redaktor-techniczny, tlumacz, copywriter, specjalista-prezentacji |
| Prawo i zgodność | prawnik, inspektor-rodo, audytor-licencji |
| Finanse | kontroler-finansowy, ksiegowy |
| Sprzedaż i marketing | strateg-marketingu, specjalista-seo, specjalista-sprzedazy, specjalista-pr |
| Operacje | obsluga-klienta, specjalista-operacji, specjalista-zakupow |
| HR | specjalista-hr, trener-szkolen |
| Badania i wiedza, Kontrola | badacz-analityk, menedzer-wiedzy, **kontroler-jakosci**, **oficer-poufnosci** |

Każdy agent ma:
- **listę dozwolonych narzędzi**, która nie obejmuje WebFetch, WebSearch ani żadnego MCP. Są trzy poziomy uprawnień: `rw` (edycja i Bash), `doc` (edycja bez Bash) oraz `ro` (tylko odczyt);
- **model dobrany do roli**: `haiku` dla ról prostych (tłumacz, PR, FAQ), `opus` dla decyzji ryzykownych (architekt, prawnik, RODO, bezpieczeństwo, kontrola jakości), a dla pozostałych `sonnet`;
- wspólne zasady: poufność, praca partiami, oszczędność tokenów i raport w maksymalnie 200 słowach.

## Poziomy poufności

**Model językowy to granica, której wtyczka nie przesunie.** Claude Code wysyła prompt oraz treść czytanych
plików do dostawcy modelu. Wtyczka nie zmienia miejsca inferencji. Może natomiast odciąć wszystkie
*pozostałe* kanały. Masz do wyboru trzy poziomy:

| Poziom | Gdzie działa model | Co wychodzi z komputera | Jak włączyć |
|---|---|---|---|
| 1 (domyślny) | Anthropic API (chmura) | tylko ruch do API modelu | `install.py --settings`; konta komercyjne (API/Team/Enterprise) domyślnie nie służą do trenowania, a dla API można zawrzeć umowę Zero Data Retention. Na kontach Free/Pro/Max wyłącz w ustawieniach prywatności udział w ulepszaniu modeli. Aktualne warunki sprawdź u dostawcy. |
| 2 | Amazon Bedrock lub Google Vertex w Twoim koncie, w regionie UE | ruch do Twojego konta chmurowego | `CLAUDE_CODE_USE_BEDROCK=1` (+ `AWS_REGION`) lub `CLAUDE_CODE_USE_VERTEX=1` (+ `CLOUD_ML_REGION`) |
| 3 (pełna lokalność) | model lokalny za bramką zgodną z API Anthropic (np. LiteLLM + Ollama/vLLM) | nic | `ANTHROPIC_BASE_URL=http://localhost:4000` i `python3 plugins/firma/tools/build_agents.py --model inherit`; jakość pracy agentowej jest wyraźnie niższa (tryb eksperymentalny) |

### Warstwy ochrony

| Warstwa | Co blokuje | Gdzie |
|---|---|---|
| Strażnik `privacy_guard.py` (hook PreToolUse) | WebFetch, WebSearch, MCP spoza `FIRMA_ALLOW_MCP` → **deny**; Bash: curl, wget, ssh, scp, nc, `git push`, publish, CLI chmur, e-mail → **deny**; instalacje pakietów, `git pull/clone`, `mvn` bez `-o`, URL-e i kod sieciowy → **ask** | wtyczka, aktywny od razu |
| `permissions.deny` | WebFetch, WebSearch, curl, wget, ssh, scp, git push | `~/.claude/settings.json` |
| Sandbox Bash (`sandbox.enabled`, `network.allowedDomains: []`) | **twarda** izolacja sieci poleceń powłoki, niezależna od heurystyk | `~/.claude/settings.json` |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` + `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_BUG_COMMAND` | telemetrię, raporty błędów, `/bug`, autoaktualizacje | `env` w ustawieniach |
| `ENABLE_CLAUDEAI_MCP_SERVERS=false` + `disableClaudeAiConnectors: true` | konektory claude.ai (Gmail, Drive, Notion…) w CLI | ustawienia |
| `cleanupPeriodDays: 14` | długie przechowywanie lokalnych transkryptów | ustawienia |
| `.firma/` w `.gitignore` | wypchnięcie planów i dzienników razem z repozytorium | projekt |

Tryby strażnika ustawiasz zmienną `FIRMA_PRIVACY`:
- `strict` (domyślny);
- `warn`, w którym wszystko podejrzane trafia do akceptacji;
- `off`.

Lokalne serwery MCP dopuszczasz zmienną `FIRMA_ALLOW_MCP="sqlite,filesystem"`.

Nie instaluj pluginów, które mają zdalne konektory. `/firma:roles-audyt` je wskaże, a wyłączysz je poleceniem `claude plugin disable <nazwa>`.
Pracuj w lokalnym Claude Code na swoim komputerze, a nie w sesjach chmurowych (claude.ai/code), bo tam repozytorium jest klonowane do kontenera dostawcy.

## Oszczędność tokenów i praca partiami

- Koszt stały wtyczki to około 2,7 tys. tokenów na sesję (opisy 47 agentów i 2 skilli; zmierzone `claude plugin details`). Hooki nie kosztują tokenów.
  Jeśli potrzebujesz mniej ról, wygeneruj podzbiór, a `kontroler-jakosci` i `oficer-poufnosci` zostaną dodani zawsze:
  `python3 plugins/firma/tools/build_agents.py --only "Inżynieria,Prawo i zgodność"`.
- `/roles` w pierwszym kroku czyta tylko indeks ról (około 1,5 tys. tokenów) i wynik `inventory.py`.
  Skrypt filtruje skille i agentów po słowach kluczowych, a z setek zewnętrznych MCP robi jedną linię.
- Subagent dostaje krótki brief ze ścieżkami plików, a nie całą rozmowę. Raport subagenta ma najwyżej 200 słów.
- Duże wejścia są dzielone na partie: około 5 plików, 1 rozdział albo 500 wierszy danych. Po każdej partii wynik jest sprawdzany, co ogranicza utratę danych i podnosi jakość.

## Rozbudowa

1. Edytuj `plugins/firma/catalog/roles.json`. Jedna rola to jeden obiekt z polami: kiedy angażować, zakres, rezultaty, skille, CLI, MCP, ścieżka babysitter i model.
2. Uruchom `python3 plugins/firma/tools/build_agents.py`. Skrypt odtworzy `agents/*.md` oraz indeks.
3. Sprawdź wynik poleceniami `claude plugin validate --strict plugins/firma` i `claude plugin details firma@firma-lokalna`.

## Co wzięto z babysitter (a5c-ai/babysitter, MIT)

Przeanalizowane elementy: `README.md`, `CLAUDE.md`, `plugins/babysitter-unified` (14 hooków, skill `babysit`, komendy),
`library/` (49 specjalizacji oraz domeny biznes, nauka i humanistyka, metodologie GSD, Spec-Kit, TDD, BMAD i inne), `packages/` (SDK, adapters, atlas, genty).

| Idea babysitter | Odpowiednik w „firmie” |
|---|---|
| Process-as-code + breakpoints | plan w partiach z punktami kontrolnymi i akceptacją „start” |
| Quality convergence (bramki jakości) | `kontroler-jakosci` (PASS/FAIL, maks. 2 iteracje poprawek) |
| Dziennik zdarzeń i wznawianie runów | `.firma/plany/*.md` i `/roles wznów` |
| Graf ról, skilli i procesów (`graph.roles`) | katalog ról i przeszukiwanie lokalnej biblioteki (`--bs`) |
| Kompresja kontekstu | briefy ze ścieżkami, filtrowana inwentaryzacja, modele per rola |

Dlaczego babysitter nie jest zależnością:
- jego hook `session-start` przy każdym starcie, gdy brakuje CLI, wykonuje `npm i -g @a5c-ai/babysitter-sdk`, czyli łączy się z siecią;
- rejestruje 14 hooków na wszystkie zdarzenia;
- wymaga Node 22.

Możesz go używać obok, po jednorazowej instalacji.

## Struktura

```
firma-plugin/
├── .claude-plugin/marketplace.json     # lokalny marketplace „firma-lokalna”
├── install.py                          # skrót /roles, ustawienia prywatności, ścieżka babysitter
└── plugins/firma/
    ├── .claude-plugin/plugin.json
    ├── agents/                         # 47 specjalistów (generowane)
    ├── catalog/roles.json              # źródło prawdy o rolach
    ├── hooks/                          # hooks.json, privacy_guard.py, session_start.py
    ├── skills/roles/                   # /firma:roles + catalog/roles-index.md + scripts/inventory.py
    ├── skills/roles-audyt/             # /firma:roles-audyt
    ├── templates/                      # settings.private.json, roles-alias.md
    └── tools/build_agents.py           # generator agentów i indeksu
```

## Ograniczenia

- Strażnik działa na wzorcach poleceń i da się go obejść, np. przez zaciemniony skrypt. Twardą granicę daje dopiero sandbox.
- Nazwy skilli w katalogu to preferencje. `/roles` pokazuje jako dostępne tylko to, co znajdzie lokalnie, a resztę oznacza jako „do instalacji”.
- Prawnik, księgowy i inspektor RODO przygotowują materiały robocze. Nie zastępują specjalisty z uprawnieniami.
