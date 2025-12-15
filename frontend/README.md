# SlovakBench Frontend

## Design Language

**Aesthetic**: Editorial / Academic Paper  
**Tone**: Serious, authoritative, quietly confident

Inšpirácia starými akademickými časopismi a typografickými postermi. Dáta hovoria samy za seba - dizajn im len ustupuje z cesty.

### Paleta

- **Cream pozadie** (`#FAFAF8`) — teplý papier, nie sterilná biela
- **Ink text** (`#1A1A1A`) — takmer čierna, jemnejšia na očiach  
- **Červený akcent** (`#E63946`) — jediný výrazný farba, používať striedmo

### Typografia

- **Space Grotesk** — geometrický grotesque pre nadpisy, evokuje technický/vedecký charakter
- **JetBrains Mono** — monospace pre dáta, čísla, labely (ALL CAPS s wide tracking pre sekcie)
- **Inter** — neutrálny sans pre bežný text

### Charakteristiky

- Minimálne tiene a efekty
- Jemné bordery (`/10` opacity)
- Pill-shaped tlačidlá s inverziou na hover
- Veľkorysé whitespace
- Staggered fade-up animácie pri načítaní

---

## Stack

Next.js 16 · Tailwind 4 · Recharts

```bash
npm run dev     # localhost:3000
```

Dáta: `uv run python main.py export` → `public/leaderboard.json`
