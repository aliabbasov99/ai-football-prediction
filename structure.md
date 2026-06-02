# AI Football Prediction - Project Structure

```
ai-football-prediction/
├── backend/                          # FastAPI backend (Python)
│   ├── main.py                       # FastAPI app, routes, pipeline
│   ├── services.py                   # Data service layer
│   ├── models.py                     # Pydantic models
│   ├── football_data_api.py          # Football data API client
│   ├── requirements.txt
│   ├── .env
│   ├── check_cleaned_db.py
│   ├── check_db.py
│   ├── print_fixtures.py
│   ├── print_predictions_doc.py
│   ├── venv/                         # Python virtual environment
│   └── scripts/
│       ├── god_mode.py               # Full pipeline orchestrator
│       ├── scrape_misli_all.py       # Misli.az odds scraping
│       ├── scrapeFootyStats.py       # FootyStats scraping
│       ├── getFixtureGames.py
│       ├── prediction_pipeline.py
│       ├── map_logos.py
│       ├── scrapSeasonGames.py
│       ├── scrape_betimate_details.py
│       ├── scrape_external_details.py
│       ├── scrape_sportsgambler_details.py
│       ├── update_prediction_links.py
│       ├── update_sportsgambler_links.py
│       └── dictionary.txt
│
├── frontend/                         # Next.js frontend (React/TypeScript)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── public/
│   │   └── imgs/
│   │       ├── flags/
│   │       ├── history/
│   │       ├── icons/
│   │       └── logos/
│   └── src/
│       ├── app/                      # Next.js App Router pages
│       │   ├── layout.tsx            # Root layout (Navbar + Footer + CouponPanel)
│       │   ├── page.tsx              # Home page
│       │   ├── globals.css           # Tailwind + custom styles
│       │   ├── admin/                # Admin pipeline page
│       │   │   ├── page.tsx
│       │   │   ├── components/
│       │   │   │   ├── PipelineReport.tsx
│       │   │   │   ├── ProgressBar.tsx
│       │   │   │   ├── Toggle.tsx
│       │   │   │   └── ...
│       │   │   └── leagues/
│       │   ├── predictions/          # Predictions page (main odds view)
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   │       ├── MatchRow.tsx
│       │   │       ├── OddsHeader.tsx
│       │   │       ├── LeagueGroup.tsx
│       │   │       ├── InlineChip.tsx
│       │   │       ├── TeamLogo.tsx
│       │   │       ├── FormBadge.tsx
│       │   │       ├── FormComparison.tsx
│       │   │       ├── BttsBox.tsx
│       │   │       ├── OverUnderBox.tsx
│       │   │       ├── PredictionsBox.tsx
│       │   │       ├── WinProbabilityBox.tsx
│       │   │       ├── LockIcon.tsx
│       │   │       ├── StandingsNeighborTable.tsx
│       │   │       ├── UpcomingAndTopScorers.tsx
│       │   │       ├── types.ts
│       │   │       └── utils.ts
│       │   ├── stats/                # Stats page
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   │       ├── FilterBar.tsx
│       │   │       ├── PredictionsTable.tsx
│       │   │       ├── StatsTable.tsx
│       │   │       ├── StatsSidebar.tsx
│       │   │       ├── GreenScoreBadge.tsx
│       │   │       ├── PercentBar.tsx
│       │   │       ├── constants.ts
│       │   │       ├── types.ts
│       │   │       └── utils.tsx
│       │   ├── schedule/             # Schedule page
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   ├── top-bottom/           # Top/Bottom matches
│       │   │   ├── page.tsx
│       │   │   └── components/
│       │   ├── footystats/           # FootyStats detail pages
│       │   │   ├── page.tsx
│       │   │   └── [slug]/
│       │   └── components/
│       │       └── StatCards.tsx
│       │
│       ├── components/               # Shared components
│       │   ├── Navbar.tsx            # Desktop navigation header
│       │   ├── Footer.tsx            # Desktop footer + Mobile tab bar
│       │   ├── CouponPanel.tsx       # Coupon slide-out panel (desktop + mobile)
│       │   ├── CouponItemRow.tsx     # Single coupon item
│       │   ├── couponUtils.ts        # Combinations, cn(), escapeHtml()
│       │   ├── LeagueSelector.tsx    # League dropdown
│       │   ├── TeamXGTable.tsx
│       │   └── StandingsTable.tsx
│       │
│       ├── context/
│       │   └── CouponContext.tsx     # Coupon state management
│       ├── lib/
│       │   ├── api.ts               # API fetch helpers
│       │   └── countries.ts         # Country flags
│       ├── types/
│       │   └── football.ts          # Shared TypeScript interfaces
│       └── constants/
│
├── data/                             # Data files
├── scratch/                          # Scratch/test scripts
├── package.json                      # Root package.json
├── run_app.bat                       # App runner script
├── plan.md                           # Project plan
├── SCRIPTS.md                        # Scripts documentation
├── CLAUDE.md                         # AI assistant instructions
├── README.md
├── structure.md                      # This file
└── all_fixtures_test.json
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend Framework | Next.js 16 + React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Icons | lucide-react |
| State Management | React Context (CouponContext) |
| Routing | Next.js App Router |
| Backend | FastAPI (Python) |
| Database | MongoDB |
| Image Export | html2canvas-oklch |




## 🖼️ Screenshots

> *(Add screenshots here to showcase the dashboard — replace these placeholders)*

<div align="center">
  <table>
    <tr>
      <td><img src="https://via.placeholder.com/400x250/1a1a2e/e94560?text=Predictions+Dashboard" alt="Predictions Dashboard" width="400"/></td>
      <td><img src="https://via.placeholder.com/400x250/1a1a2e/0f3460?text=Betting+Coupon" alt="Betting Coupon" width="400"/></td>
    </tr>
    <tr>
      <td align="center"><strong>Predictions Dashboard</strong></td>
      <td align="center"><strong>Betting Coupon</strong></td>
    </tr>
    <tr>
      <td><img src="https://via.placeholder.com/400x250/1a1a2e/533483?text=Stats+Page" alt="Stats Page" width="400"/></td>
      <td><img src="https://via.placeholder.com/400x250/1a1a2e/e94560?text=Admin+Panel" alt="Admin Panel" width="400"/></td>
    </tr>
    <tr>
      <td align="center"><strong>Statistical Analysis</strong></td>
      <td align="center"><strong>Admin Control Panel</strong></td>
    </tr>
  </table>
</div>

---
