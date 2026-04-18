# AI Football Prediction - Plan

## 1. Layihə Məqsədi

Futbol matçlarının proqnozlaşdırılması üçün analitik platforma.
Hədəf: Ev/Dışı/Ümumi statistika, xG analizi, kart/korner statistikası, PPDA əsaslı Over/Under proqnozları.

## 2. Layihə Strukturu

```
ai-football-prediction/
├── frontend/                 # Next.js + Tailwind CSS
│   ├── src/
│   │   ├── app/            # Ana səhifə, layout
│   │   ├── components/      # UI komponentləri
│   │   ├── lib/            # API client
│   │   └── types/          # TypeScript tipləri
│   └── package.json
│
├── backend/                 # FastAPI
│   ├── main.py             # API endpointləri
│   ├── models.py           # Pydantic modelləri
│   ├── services.py         # Data fetching
│   └── requirements.txt
│
└── plan.md
```

## 3. Pulsuz Mənbələr

### Ana Mənbələr

| Mənbə | Pulsuz Limit | xG | Kart | Korner | PPDA | Liqalar |
|-------|--------------|-----|------|--------|------|---------|
| **BSD API** (sports.bzzoiro.com) | Limitsiz | ✅ | ✅ | ✅ | ❌ | 34 |
| **Understat** (scraping) | Tam pulsuz | ✅ | ❌ | ❌ | ✅ | 6 |
| **API-Football** (RapidAPI) | 100/gün | ❌ | ✅ | ✅ | ✅ | 1100+ |
| **SportSRC** | 1000/gün | ❌ | ✅ | ✅ | ❌ | 50+ |

### BSD API - Əsas Seçim
- **Limitsiz sorğu**, API açarı tələb olunmur
- xG, shot maps, canlı hesablar
- ML proqnozları daxili (Over/Under 1.5/2.5/3.5, BTTS)
- 34 liqa: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie

### Understat - xG/PPDA üçün
- **Tam pulsuz**, scraping ilə işləyir
- `pip install understatapi`
- 6 əsas Avropa liqası
- xG, xA, xGChain, PPDA oxşar metriklər

## 4. Hazırkı Vəziyyət ✅

### Tamamlananlar:
- [x] Frontend struktur (Next.js + Tailwind CSS)
- [x] Backend struktur (FastAPI)
- [x] Ana səhifə - Komanda xG analizi
- [x] Liqa seçicisi
- [x] TeamXGTable komponenti (Son 30 oyun, Liqa, Kubok xG)
- [x] Backend API endpointləri
- [x] Mock data (BSD API əvəzinə)

### Ana Səhifə Xüsusiyyətləri:
- Liqa seçimi (6 liqa)
- Komanda cədvəli hər komanda üçün:
  - Son 30 oyun xG (For/Against/Games)
  - Liqa xG (For/Against/Games)
  - Kubok xG (For/Against/Games)
  - Forma (W/D/L)
  - Cədvəldə yeri

## 5. Texniki Stack

```
frontend/
├── Next.js 16
├── Tailwind CSS
├── TypeScript
└── TanStack Query

backend/
├── Python FastAPI
├── httpx (async HTTP)
└── Pydantic v2
```

## 6. API Endpoint-ləri

```
GET /api/health                    - Sağlamlıq yoxlaması
GET /api/leagues                   - Liqalar siyahısı
GET /api/leagues/{id}/teams       - Komanda xG statistikası
GET /api/leagues/{id}/top-bottom  - Top vs Bottom matçları
GET /api/teams/{id}               - Bir komandanın məlumatı
GET /api/matches/live              - Canlı matçlar
```

## 7. Növbəti Addımlar

### Fazə 2: İnkişaf
- [ ] BSD API real inteqrasiya
- [ ] Kart statistikası səhifəsi
- [ ] Korner statistikası səhifəsi
- [ ] Top/Bottom 50 matç siyahısı
- [ ] PPDA analizi

### Fazə 3: Proqnozlar
- [ ] Over/Under proqnoz səhifəsi
- [ ] BTTS proqnozu
- [ ] ML model inteqrasiyası
- [ ] H2H analiz

### Fazə 4: Genişlənmə
- [ ] Ev/Deplesman statistika ayrılması
- [ ] Understat scraping (xG, PPDA)
- [ ] Kart/Korner API-Football
- [ ] Canlı matçlar səhifəsi

## 8. İşə Salma

### Backend:
```bash
cd backend
python main.py
# http://localhost:8000
```

### Frontend:
```bash
cd frontend
npm run dev
# http://localhost:3000
```

## 9. Dəyər Təhlili

| Mənbə | Ayda Dəyər |
|-------|-----------|
| BSD API | $0 |
| Understat | $0 |
| API-Football (pulsuz) | $0 |
| **Cəmi** | **$0** |

Tamamilə pulsuz inkişaf!
