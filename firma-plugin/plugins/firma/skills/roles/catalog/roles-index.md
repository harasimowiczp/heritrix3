# Katalog ról firmy (indeks)

Format: `id` [dział · model · uprawnienia] — kiedy angażować | preferowane skille


## Zarząd
- `strateg-ceo` [opus · doc] — decyzje go/no-go, priorytety, model biznesowy, trade-offy między działami | product-management:brainstorm, operations:risk-assessment, anthropic-skills:llm-council
- `kierownik-projektu` [sonnet · doc] — plan, harmonogram, podział na partie, RACI, ryzyka, statusy | productivity:task-management, operations:status-report, product-management:sprint-planning
- `analityk-biznesowy` [sonnet · doc] — wymagania, user stories, procesy, kryteria akceptacji, analiza luk | product-management:write-spec, operations:process-doc
- `product-manager` [sonnet · doc] — PRD, roadmapa, priorytetyzacja funkcji, metryki produktu | product-management:write-spec, product-management:roadmap-update, product-management:metrics-review

## Inżynieria
- `architekt-oprogramowania` [opus · doc] — architektura, dobór technologii, ADR, skalowalność, integracje systemów | engineering:architecture, engineering:system-design
- `backend-developer` [sonnet · rw] — API, logika biznesowa, bazy danych, Java/Python/Node/Go, serwisy | engineering:debug, engineering:testing-strategy
- `frontend-developer` [sonnet · rw] — UI webowe, React/Vue/Angular, CSS, komponenty, wydajność strony | modern-web-guidance:modern-web-guidance, anthropic-skills:web-artifacts-builder
- `mobile-developer` [sonnet · rw] — aplikacje iOS/Android, Flutter, React Native, Kotlin, Swift | —
- `inzynier-danych` [sonnet · rw] — ETL/ELT, pipeline'y, hurtownie, jakość danych, CSV/Parquet | data:validate-data, data:sql-queries
- `administrator-baz-danych` [sonnet · rw] — schemat bazy, indeksy, wolne zapytania, migracje, backup | data:write-query
- `devops-inzynier` [sonnet · rw] — CI/CD, Docker, Kubernetes, IaC, monitoring, wdrożenia, niezawodność | engineering:deploy-checklist, operations:runbook, engineering:incident-response
- `inzynier-qa` [sonnet · rw] — strategia testów, testy E2E/integracyjne, regresja, pokrycie | engineering:testing-strategy
- `specjalista-bezpieczenstwa` [opus · rw] — OWASP, sekrety w kodzie, podatności zależności, threat modeling, uwierzytelnianie | security-review, engineering:code-review
- `recenzent-kodu` [sonnet · ro] — przegląd zmian, jakość kodu, czytelność, błędy logiczne przed scaleniem | code-review, simplify
- `inzynier-wydajnosci` [sonnet · rw] — wolne działanie, profilowanie, pamięć, testy obciążeniowe, optymalizacja | —
- `specjalista-migracji` [sonnet · rw] — legacy, aktualizacja frameworka/języka, migracja platformy, dług techniczny | engineering:tech-debt
- `inzynier-ai` [sonnet · rw] — modele ML, LLM, RAG, embeddingi, ewaluacja modeli, lokalne modele | claude-api
- `inzynier-integracji` [sonnet · rw] — integracja systemów, własny serwer MCP, CLI, automatyzacja, webhooki | anthropic-skills:mcp-builder, anthropic-skills:skill-creator

## Dane i analityka
- `analityk-danych` [sonnet · rw] — analiza danych, SQL, Excel/CSV, raporty, KPI, trendy | data:analyze, data:explore-data, anthropic-skills:xlsx, dataviz
- `data-scientist` [sonnet · rw] — statystyka, testy A/B, prognozy, modele predykcyjne, segmentacja | data:statistical-analysis
- `specjalista-bi` [sonnet · rw] — dashboard, wykresy, raport zarządczy, wizualizacja KPI | data:build-dashboard, data:create-viz, dataviz

## Projektowanie
- `projektant-ux` [sonnet · doc] — ścieżki użytkownika, architektura informacji, badania, persony, użyteczność | design:user-research, design:research-synthesis, design:design-critique
- `projektant-ui` [sonnet · rw] — wygląd, design system, tokeny, komponenty wizualne, przekazanie do developmentu | design:design-system, design:design-handoff, anthropic-skills:theme-factory
- `specjalista-dostepnosci` [sonnet · rw] — WCAG, czytniki ekranu, kontrast, nawigacja klawiaturą, ustawa o dostępności | design:accessibility-review
- `ux-writer` [haiku · doc] — teksty w interfejsie, komunikaty błędów, onboarding, microcopy | design:ux-copy, brand-voice:enforce-voice

## Dokumentacja i treści
- `redaktor-techniczny` [sonnet · doc] — dokumentacja, README, instrukcje, API docs, procedury | engineering:documentation, anthropic-skills:docx, anthropic-skills:pdf, anthropic-skills:doc-coauthoring
- `tlumacz` [haiku · doc] — tłumaczenie, lokalizacja, i18n, wersje językowe dokumentów | —
- `copywriter` [sonnet · doc] — teksty marketingowe, artykuły, newsletter, opisy produktów, korekta | marketing:draft-content, marketing:content-creation, brand-voice:enforce-voice
- `specjalista-prezentacji` [sonnet · rw] — prezentacja, PowerPoint, raport Word, arkusz Excel, PDF do druku | anthropic-skills:pptx, anthropic-skills:docx, anthropic-skills:xlsx, anthropic-skills:pdf

## Prawo i zgodność
- `prawnik` [opus · doc] — umowa, NDA, regulamin, własność intelektualna, odpowiedzialność, spór | legal:review-contract, legal:triage-nda, legal:legal-risk-assessment, small-business:contract-review
- `inspektor-rodo` [opus · doc] — RODO/GDPR, dane osobowe, DPIA, polityki, NIS2, AI Act, audyt zgodności | legal:compliance-check, operations:compliance-tracking
- `audytor-licencji` [haiku · rw] — licencje zależności, SBOM, zgodność GPL/MIT/Apache, NOTICE | —

## Finanse
- `kontroler-finansowy` [sonnet · rw] — budżet, prognoza, rentowność, unit economics, analiza odchyleń, wycena | finance:variance-analysis, finance:financial-statements, anthropic-skills:xlsx
- `ksiegowy` [sonnet · rw] — księgowania, uzgodnienia, VAT, JPK, faktury, zamknięcie miesiąca | finance:reconciliation, finance:journal-entry-prep, finance:close-management

## Sprzedaż i marketing
- `strateg-marketingu` [sonnet · doc] — strategia marketingowa, kampania, pozycjonowanie, segmentacja, persona klienta | marketing:campaign-plan, marketing:competitive-brief, small-business:content-strategy
- `specjalista-seo` [sonnet · rw] — SEO, widoczność w wyszukiwarkach i AI, meta tagi, struktura treści | marketing:seo-audit
- `specjalista-sprzedazy` [sonnet · doc] — oferta, propozycja handlowa, wycena, obiekcje, przygotowanie do rozmowy | sales:create-an-asset, sales:handle-objection, small-business:proposal-builder
- `specjalista-pr` [haiku · doc] — komunikat prasowy, komunikacja wewnętrzna, kryzys, ogłoszenie | anthropic-skills:internal-comms

## Operacje
- `obsluga-klienta` [haiku · doc] — FAQ, baza wiedzy, szablony odpowiedzi, reklamacje, zgłoszenia | small-business:ticket-deflector
- `specjalista-operacji` [sonnet · doc] — procedury SOP, optymalizacja procesów, runbooki, zarządzanie zmianą | operations:process-doc, operations:process-optimization, operations:change-request
- `specjalista-zakupow` [haiku · doc] — wybór dostawcy, porównanie ofert, RFP, ocena vendora, TCO | operations:vendor-review, legal:vendor-check

## HR
- `specjalista-hr` [sonnet · doc] — rekrutacja, ogłoszenie o pracę, onboarding, ocena pracownicza, regulamin pracy | human-resources:recruiting-pipeline, human-resources:onboarding, human-resources:performance-review
- `trener-szkolen` [haiku · doc] — szkolenie, materiały edukacyjne, quiz, instrukcja krok po kroku | anthropic-skills:pptx

## Badania i wiedza
- `badacz-analityk` [opus · doc] — research na lokalnych dokumentach, synteza źródeł, porównanie rozwiązań, raport | enterprise-search:knowledge-synthesis
- `menedzer-wiedzy` [haiku · doc] — baza wiedzy, notatki, indeks dokumentów, porządkowanie informacji | desktop-commander:knowledge-base, productivity:memory-management

## Kontrola
- `kontroler-jakosci` [opus · ro] — weryfikacja wyników innych ról, fact-checking, bramka jakości przed oddaniem | —
- `oficer-poufnosci` [haiku · ro] — czy plan lub narzędzie wysyła dane na zewnątrz, audyt narzędzi, przegląd przed udostępnieniem | —
