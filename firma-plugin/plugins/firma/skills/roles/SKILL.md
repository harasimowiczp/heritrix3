---
name: roles
description: Analizuje zadanie z czatu i proponuje zespół specjalistów firmy (47 ról), skille, pluginy, MCP i narzędzia offline, z planem w partiach i oceną poufności. Użyj, gdy użytkownik wpisze /firma:roles lub /roles albo poprosi o dobór ról/narzędzi do zadania.
argument-hint: "[opis zadania] | katalog | wznów"
allowed-tools: Read, Glob, Grep, Bash(python3:*), Write, Edit
---

# /roles — dobór zespołu i narzędzi (tryb poufny, lokalny)

Zadanie użytkownika: $ARGUMENTS

Jeśli powyżej jest pusto — użyj zadania opisanego ostatnio w czacie. Jeśli go brak — zapytaj jednym zdaniem i zakończ.

## Tryby
- `katalog` → wyświetl `${CLAUDE_SKILL_DIR}/catalog/roles-index.md` i zakończ.
- `wznów` → wczytaj najnowszy plik z `.firma/plany/`, pokaż status partii i kontynuuj od pierwszej niezakończonej.
- w pozostałych przypadkach → kroki 1–4.

## Krok 1 — dane (jedna tura, równolegle)
1. Przeczytaj `${CLAUDE_SKILL_DIR}/catalog/roles-index.md`.
2. Uruchom `python3 "${CLAUDE_SKILL_DIR}/scripts/inventory.py" --match "<5–10 słów kluczowych PL i EN>" --bs "<3–6 słów EN>"`
   (słowa wyprowadź z zadania; `--bs` działa tylko, gdy ustawiono `FIRMA_BABYSITTER_LIB`).

Nie czytaj innych plików na tym etapie — oszczędzaj tokeny.

## Krok 2 — analiza
- Cel, rezultat końcowy, kryteria akceptacji (jeśli brak — zaproponuj).
- Złożoność S/M/L i wrażliwość danych. Domyślnie traktuj projekt jako POUFNY.
- Wybierz **minimalny** zespół: S → 1–2 role, M → 3–4, L → 5–7. Każda rola musi mieć jasny rezultat.
- Narzędzia: najpierw zainstalowane (z inwentaryzacji), potem z katalogu. Skill to lokalne instrukcje — po instalacji działa offline; konektor/MCP zdalny to wysyłka danych.
- Wszystko oznaczone ZEWNĘTRZNY, konektory claude.ai, WebFetch/WebSearch → ⛔ i podaj zamiennik lokalny (np. ręczny eksport pliku, lokalny MCP stdio, CLI offline).
- Duże wejścia dziel na partie (ok. 5 plików / 1 rozdział / 500 wierszy danych) — mniejsza utrata informacji i wyższa jakość.

## Krok 3 — propozycja (zwięźle, bez powtarzania treści zadania)

```
## Analiza
Cel: … | Rezultat: … | Złożoność: S/M/L | Wrażliwość: … (dlaczego)
Kryteria akceptacji: 1) … 2) …
Pytania (maks. 3, tylko blokujące): …

## Zespół
| Agent | Odpowiada za | Model | Partie |

## Narzędzia
| Narzędzie | Typ | Do czego | Status |
Status: ✅ dostępne · ➕ warto doinstalować (lokalne) · ⛔ odrzucone (zewnętrzne) → zamiennik

## Plan w partiach
1. [agent] wejście → rezultat (plik) — punkt kontrolny
…
Bramka jakości: kontroler-jakosci; przy wrażliwości ≥ średniej także oficer-poufnosci.

## Koszt
Szacunek tokenów/czasu i jak go ograniczono (modele haiku dla prostych ról, partie, brief zamiast całego czatu).

Odpowiedz: **start** · **zmień …** · **zapisz**
```

Na tym kończysz turę — nic nie wykonujesz przed akceptacją.

## Krok 4 — po akceptacji („start”)
1. Zapisz plan do `.firma/plany/RRRR-MM-DD-<slug>.md` (dziennik: plan + status partii). Jeśli `.firma/` nie ma w `.gitignore`, zaproponuj dopisanie.
2. Deleguj partie narzędziem Agent (`subagent_type`: `firma:<id>`). Każdy brief jest samowystarczalny i krótki: cel, ścieżki wejściowe, kryteria akceptacji, ścieżka wyniku. Nie wklejaj całej rozmowy ani zawartości plików — podaj ścieżki.
3. Niezależne partie uruchamiaj równolegle; zależne — kolejno.
4. Po każdej partii dopisz do dziennika 1–3 linie statusu. Zatrzymaj się na punkcie kontrolnym tylko wtedy, gdy wynik wymaga decyzji użytkownika.
5. Na końcu uruchom bramkę jakości. FAIL → popraw wskazane elementy (maks. 2 iteracje), potem raport.
6. Raport końcowy: rezultaty (ścieżki), weryfikacja, otwarte ryzyka — maks. 15 linii.

## Zasady
- Żadnych danych projektu poza komputerem: bez WebFetch/WebSearch, zdalnych MCP i poleceń sieciowych (strażnik `privacy_guard` i tak je blokuje).
- Nie wymyślaj nazw skilli ani pluginów — tylko z inwentaryzacji lub katalogu (te drugie oznacz ➕).
- Gdy pasuje proces z biblioteki babysitter, podaj ścieżkę jako procedurę dla partii; agent czyta tylko potrzebny fragment.
