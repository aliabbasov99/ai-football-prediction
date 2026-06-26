# Deployment Bələdçisi

## Memarlıq

```
[İstifadəçi] → Vercel (Next.js Frontend)
                       ↓ (API sorğuları)
                  Backend Server (FastAPI + Telegram Bot)
                       ↓
                  MongoDB (Atlas və ya VPS-də)
```

- **Frontend**: Next.js 16 — Vercel-ə deploy olunur
- **Backend**: FastAPI (Python) — VPS və ya Railway/Render/Host maral kimi xidmətdə işləyir
- **Telegram Bot**: Backend-lə eyni serverdə ayrı proses kimi işləyir
- **MongoDB**: MongoDB Atlas (pulsuz) və ya VPS-də self-hosted

---

## 1. MongoDB (Atlas)

1. https://www.mongodb.com/atlas — qeydiyyatdan keç
2. **Free cluster** yarat
3. **Database Access** → istifadəçi adı + şifrə yarat
4. **Network Access** → backend server-in IP ünvanını əlavə et (və ya `0.0.0.0/0` — bütün IP-lər, amma təhlükəsizlik üçün şifrə güclü olmalıdır)
5. **Connect** → connection string-i kopyala: `mongodb+srv://user:pass@cluster.mongodb.net/`

---

## 2. Backend (FastAPI)

### Seçim A: VPS (Linux server)

```bash
# Server-ə daxil ol (SSH)
ssh user@server_ip

# Dependency-lər
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Chrome + ChromeDriver (Selenium üçün)
sudo apt install -y google-chrome-stable

# Reponu klonla
git clone https://github.com/yourusername/ai-football-prediction.git
cd ai-football-prediction/backend

# Virtual mühit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env faylı yarat
nano .env
```

`.env` faylı:
```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
JWT_SECRET_KEY=güclü-təsadüfi-açar
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
BOT_SECRET=qolqol-bot-secret-2024
```

```bash
# Backend-i işə sal (port 7999)
nohup venv/bin/python main.py > backend.log 2>&1 &

# Telegram botu işə sal
cd ../telegram-bot
nohup /usr/bin/python3 bot.py > bot.log 2>&1 &
```

### Seçim B: Railway / Render

Railway və ya Render-də **Python** service yarat:

- **Root directory**: `backend/`
- **Start command**: `python main.py`
- **Env vars**: `MONGODB_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_HOURS`, `BOT_SECRET`
- **Port**: `7999`

> **Qeyd**: Railway/Render-də Selenium (ChromeDriver) işləməyə bilər. Scraping funksiyaları üçün VPS lazımdır.

---

## 3. Frontend (Vercel)

### 3.1 `next.config.ts`-i yenilə

API proxy `127.0.0.1:7999`-i göstərir — Vercel-də işləməz. Backend-in real URL-ini yaz:

```ts
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'https://backend-url.com/api/:path*',  // Backend-in URL-i
    },
  ];
},
```

### 3.2 Vercel-ə deploy

```bash
# 1. GitHub/GitLab repo-ya push et

# 2. Vercel-ə daxil ol → Add New Project → GitHub repo-nu seç

# 3. Root Directory: frontend/
#    Build: next build
#    Output: .next

# 4. Environment Variables (əlavə etməyə ehtiyac yoxdur — frontend-in .env faylı yoxdur)

# 5. Deploy
```

### 3.3 Custom Domain (istəyə bağlı)

Vercel dashboard → Project Settings → Domains → öz domain-ini əlavə et.

---

## 4. Telegram Bot

Telegram bot backendlə eyni serverdə işləyir. Bot token-lərini `telegram-bot/bot.py` faylında dəyiş.

```bash
cd telegram-bot
nohup /usr/bin/python3 bot.py > bot.log 2>&1 &
```

Bot-un `API_BASE_URL` dəyərini backend-in real URL-i ilə yenilə:
```python
API_BASE_URL = "https://backend-url.com"  # localhost:7999 deyil
```

---

## 5. Tam Yoxlama Siyahısı

| Komponent | Harada | Port |
|-----------|--------|------|
| MongoDB Atlas | Cloud | 27017 |
| FastAPI Backend | VPS / Railway | 7999 |
| Telegram Bot | VPS | — |
| Next.js Frontend | Vercel | 443 (HTTPS) |
| Custom Domain | Vercel DNS | 443 |

### Addımlar:

1. ✅ MongoDB Atlas cluster yarat, connection string-i `.env`-ə yaz
2. ✅ Backend-i VPS-də işə sal (`python main.py`)
3. ✅ Telegram bot-u işə sal (`python bot.py`)
4. ✅ `next.config.ts`-də proxy URL-i backend-in real URL-inə dəyiş
5. ✅ Frontend-i Vercel-ə deploy et
6. ✅ Hər şey işləyir — test et: frontend URL → daxil ol → məlumatlar gəlir
