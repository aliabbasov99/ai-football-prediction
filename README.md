<div align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js" alt="Next.js 16">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React 19">
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb" alt="MongoDB">
  <img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=for-the-badge&logo=tailwindcss" alt="Tailwind CSS 4">
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript 5">
</div>

# ⚽ AI Football Prediction

> **Multi-source football match predictions, live odds aggregation, and betting analytics platform.**

AI Football Prediction is a full-stack application that **scrapes odds, predictions, and statistics** from 7+ betting/external websites, stores everything in MongoDB, and serves it through a modern web dashboard. Built for football enthusiasts, data analysts, and betting strategists.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Source Aggregation** | Combines odds & predictions from Misli.az, Betimate, SportsGambler, WinComparator, Oddslot, WhoScored, and FootyStats |
| **Web Scraping Pipeline** | Automated Selenium-based pipeline with progress tracking — configure which steps to run |
| **Smart Team Matching** | Fuzzy alias-based team name resolution across all sources (normalization + Levenshtein) |
| **Live Predictions Dashboard** | Filterable, league-grouped view of upcoming matches with all odds side-by-side |
| **Betting Coupon** | Virtual betting slip with system bet calculator, stake management, and PNG export |
| **FootyStats Integration** | 18+ statistical categories (BTTS, O/U goals, corners, cards) with per-match breakdowns |
| **Top vs Bottom Analysis** | Identify fixtures where top-table teams face bottom-table opposition |
| **Standings Intelligence** | League tables with form badges, xG stats, and champion/relegation zone cards |
| **Admin Control Panel** | Start/stop individual pipeline steps, clear database, manage leagues and team aliases |
| **Azerbaijan Optimized** | Asia/Baku timezone, local flag assets, localized team name dictionary |

---

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

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                   Frontend                        │
│              Next.js 16 + React 19                │
│      Tailwind CSS 4 + TypeScript 5 + Lucide       │
│          ┌────────────────────────────┐            │
│          │   API Proxy (rewrites)     │            │
│          │   /api/* → :7999/*         │            │
│          └──────────┬─────────────────┘            │
└─────────────────────┼────────────────────────────┘
                      │ HTTP (REST)
┌─────────────────────┼────────────────────────────┐
│          ┌──────────┴─────────────────┐            │
│          │   FastAPI Backend (:7999)   │            │
│          │   Python 3.13 + Pydantic    │            │
│          └──────────┬─────────────────┘            │
│                     │                              │
│          ┌──────────┴─────────────────┐            │
│          │   DataService (cached)      │            │
│          └──────────┬─────────────────┘            │
│                     │                              │
│          ┌──────────┴─────────────────┐            │
│          │   Scraping Pipeline         │            │
│          │   (Selenium + BS4 + httpx)  │            │
│          └─────────────────────────────┘            │
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────┴────────────────────────────┐
│              MongoDB (football_prediction)         │
│   standings │ fixtures │ matches │ teams │ pages   │
└──────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.13** — Core language
- **FastAPI** — REST API framework (port 7999)
- **Pydantic v2** — Data validation & models
- **MongoDB + PyMongo** — Database
- **Selenium / undetected-chromedriver** — Web scraping
- **BeautifulSoup4** — HTML parsing
- **httpx + requests** — HTTP clients
- **Uvicorn** — ASGI server

### Frontend
- **Next.js 16** — React framework (App Router)
- **React 19** — UI library
- **TypeScript 5** — Type safety
- **Tailwind CSS 4** — Utility-first styling
- **Lucide React** — Icon library
- **html2canvas-oklch** — Coupon export as image

### DevOps
- **Git** — Version control
- **ESLint** — Frontend linting
- **Ruff** — Python linting

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | ≥ 3.13 | Backend runtime |
| Node.js | ≥ 20 | Frontend runtime |
| MongoDB | ≥ 7 | Database (localhost:27017) |
| Chrome | latest | Web scraping driver |

### 1️⃣ Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Configure your database connection in `backend/.env`:

```env
MONGODB_URL=mongodb://localhost:27017
```

Start the backend:

```bash
python main.py
# → Server running at http://localhost:7999
```

### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
# → Server running at http://localhost:3000
```

### 3️⃣ Quick Launch (Windows)

Double-click `run_app.bat` — it launches both servers in separate terminal windows.

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI entry point & REST endpoints
│   ├── services.py             # DataService — MongoDB queries with caching
│   ├── models.py               # Pydantic models (GameStats, Match, etc.)
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment config
│   └── scripts/
│       ├── god_mode.py         # Pipeline orchestrator
│       ├── scrapeFootyStatsGames.py
│       ├── scrapeFootyStats.py
│       ├── scrape_misli_all.py
│       ├── scrape_betimate_details.py
│       ├── scrape_sportsgambler_details.py
│       ├── scrape_external_details.py
│       ├── update_prediction_links.py
│       └── map_logos.py
│
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   │   ├── page.tsx        # Home — league selector + xG table
│   │   │   ├── predictions/    # Odds & predictions dashboard
│   │   │   ├── stats/          # FootyStats statistical data
│   │   │   ├── schedule/       # League standings
│   │   │   ├── top-bottom/     # Top vs bottom matchups
│   │   │   ├── footystats/     # FootyStats page index
│   │   │   └── admin/          # Pipeline control panel
│   │   ├── components/         # Shared UI components
│   │   ├── context/            # CouponContext (betting slip)
│   │   ├── lib/                # API helpers & utilities
│   │   └── types/              # TypeScript interfaces
│   ├── public/imgs/            # Flags, logos, icons
│   ├── package.json
│   └── next.config.ts
│
├── data/                       # Sample data files
├── CLAUDE.md                   # AI assistant guidelines
├── run_app.bat                 # Windows launcher
└── README.md                   # You are here 🎯
```

---

## 🔌 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/leagues` | List all leagues with metadata |
| `GET` | `/api/leagues/{id}/teams` | Team xG stats for a league |
| `GET` | `/api/predictions` | All predictions with odds |
| `GET` | `/api/top-bottom/teams` | Top & bottom teams across leagues |
| `GET` | `/api/top-bottom/matches` | Top-vs-bottom upcoming fixtures |
| `GET` | `/api/matches/live` | Live match data |
| `GET` | `/api/footystats/pages` | FootyStats page index |
| `GET` | `/api/footystats/page/{slug}` | Specific stat page data |
| `GET` | `/api/admin/status-live` | Pipeline status (SSE-ready) |
| `POST` | `/api/admin/scrape-start` | Start scraping pipeline |
| `POST` | `/api/admin/clear-db` | Drop all collections |
| `POST` | `/api/admin/leagues` | Create league config |
| `PUT` | `/api/admin/leagues/{id}` | Update league config |
| `DELETE` | `/api/admin/leagues/{id}` | Delete league |

---

## 🤝 Contributing

Contributions are welcome! This is a hobby project with room for improvement:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing`)
5. **Open** a Pull Request

**Ideas for contributions:**
- Add new data sources / scrapers
- Improve fuzzy team matching accuracy
- Add ML-based prediction models
- WebSocket-based live updates
- Docker Compose setup for one-command deploy
- Mobile app (React Native / Flutter)

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**. Odds and predictions are aggregated from publicly available sources — always gamble responsibly. The authors are not responsible for any financial losses incurred through use of this software.

---

<div align="center">
  <sub>Built with ❤️ for football analytics enthusiasts</sub>
  <br>
  <a href="#">Report Bug</a> · <a href="#">Request Feature</a>
</div>
