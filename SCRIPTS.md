# Skriptlər Sənədi

## Backend Skriptləri (`backend/scripts/`)

### `scrapSeasonGames.py`
Lig sıralama cədvəllərini (standings) WhoScored-dan Selenium ilə qaşıyır. Hər komanda üçün sıra, ad, oyun/qalibiyyət/heç-heçə/məğlubiyyət, atılan/buraxılan qol, qol fərqi, xal və son forma məlumatlarını MongoDB `standings` kolleksiyasına yazır. `run_all_combined()` rejimində standings və fixtures-i eyni brauzer sessiyasında qaşıyır.

### `getFixtureGames.py`
Qarşıdakı oyunların cədvəlini (tarix, saat, ev/qonaq komanda) WhoScored-dan Selenium ilə qaşıyır. Nəticələri MongoDB `fixtures` kolleksiyasına saxlayır (hər liqa üçün köhnə məlumatı təmizləyib) və ehtiyat olaraq `all_fixtures_test.json` faylına yazır.

### `god_mode.py`
Bütün pipeline-i idarə edən master skript: ardıcıl olaraq standings, fixtures, prediction link (WinComparator, Oddslot, Betimate, SportsGambler, FootyStats) yeniləmə və detal qaşıma addımlarını işlədir. Hər addımı açıb-söndürmək üçün toggle dəstəkləyir, progress callback və yekun hesabat (neçə fixture-in linki/proqnozu var) verir.

### `prediction_pipeline.py`
Sadə orkestrator – yalnız iki detal skriptini (`scrape_betimate_details` + `scrape_sportsgambler_details`) ardıcıl işlədir. Link-lərin artıq bazada olduğunu fərz edir.

### `update_prediction_links.py`
WinComparator, Oddslot, Betimate, SportsGambler, FootyStats saytlarından bugün/sabahkı oyunlar üçün proqnoz səhifəsi linklərini qaşıyır. Hər mənbənin listing səhifəsinə girir, komanda adlarını alias sistemi ilə fuzzy match edir və linkləri MongoDB `predictions.*_link` sahələrinə yazır.

### `update_sportsgambler_links.py`
Legacy versiya – yalnız SportsGambler "betting tips" səhifəsindən link qaşıyır. `update_prediction_links.py`-dəki sportsgambler addımının sadələşmiş variantıdır.

### `scrape_betimate_details.py`
Hər fixture-in Betimate proqnoz linkini açır (undetected_chromedriver ilə). Qələbə/heç-heçə/məğlubiyyət ehtimalları, under/over 2.5 əmsalları, BTTS faizləri, hər iki komandanın növbəti oyunları və ən yaxşı qolçuları qaşıyır. MongoDB `predictions.betimate_stats`-a yazır.

### `scrape_sportsgambler_details.py`
Hər fixture-in SportsGambler proqnoz linkini açır. Matç proqnozu mətni (məs. "Under 2.5 Goals @ 2.07") və dəqiq hesab proqnozunu çıxarır. MongoDB `predictions.sportsgambler_stats`-a yazır.

### `scrape_external_details.py`
Çoxməqsədli detal skripti. Üç alt rejimi var:
- **FootyStats H2H**: head-to-head müqayisə çubuqları, stat qridləri, komanda form bölmələri
- **WinComparator**: 1X2 proqnozları, under/over xətləri, BTTS proqnozları (ehtimal+əmsal)
- **Oddslot**: listing səhifələrindən qələbə faizlərini qaşıyır
`--step` argumenti ilə hansı rejimin işləyəcəyi seçilir.

### `scrape_misli_all.py`
Misli.az saytından 1X2, double chance, under/over, BTTS əmsallarını qaşıyır. Undetected_chromedriver ilə liqa kateqoriya ağacında XPATH kliklərlə gəzir. Azərbaycanca komanda adlarını `dictionary.txt` və DB alias kolleksiyası (fuzzy match) vasitəsilə ingiliscə adlara çevirir.

### `scrapeFootyStats.py`
FootyStats.org saytındakı bütün stat səhifələrini (BTTS, under/over, korner, kart, refere, clean sheet, ümumi hesab, proqnozlar) kütləvi şəkildə qaşıyır. Nəticələri `footystats_pages` (strukturlu) və `footystats_all` (düzəldilmiş) kolleksiyalarına yazır. Hər 4 səhifədən sonra Chrome driver-ı dəyişdirir.

### `map_logos.py`
Komanda adlarını `standings` kolleksiyasından `frontend/public/imgs/logos/` qovluğundakı loqo fayllarına eşləyir. `team_logo` sahəsini yeniləyir. Ad uyğunlaşdırma üçün alias lüğəti, substring və fuzzy matching istifadə edir.

---

## Backend Əsas Faylları

### `main.py`
FastAPI ilə qurulmuş backend server. API vasitəsilə liqalar, komandalar, xG statistikası, proqnozlar və canlı matçlar üçün endpoint-lər təqdim edir. Həmçinin admin panel üçün scraping işə salma, bazanı təmizləmə, liqa/komanda CRUD endpoint-ləri var. Pipeline vəziyyətini izləmək üçün `status-live` və `status` endpoint-ləri mövcuddur.

### `services.py`
Məlumat xidməti təbəqəsi. MongoDB-dən liqa, komanda statistikası, fixturlər, proqnozlar sorğulayır. xG hesablamaları, top/bottom komanda seçimi, keşləmə və loqo eşlemə məntiqini ehtiva edir. `DataService` sinfi `get_teams_stats()`, `get_top_bottom_matches()`, `get_predictions()` kimi metodlarla API-yə xidmət edir.

### `models.py`
Pydantic məlayat modelləri: `GameStats`, `TeamXGStats`, `League`, `Last5Game`, `Match`, `Prediction`. API cavab sxemi kimi xidmət edir.

---

## Digər Fayllar

### `run_app.bat`
Windows batch faylı. Backend (FastAPI) və frontend (Next.js) serverlərini eyni anda ayrı pəncərələrdə işə salır.

### `backend/football_data_api.py`
Ehtimal ki, alternativ/data mənbəyi API skripti (əlavə məlumat üçün yoxlanılmalıdır).

### `backend/check_db.py` / `backend/check_cleaned_db.py`
MongoDB bazasındakı məlumatları yoxlamaq üçün util skriptləri.

### `backend/print_fixtures.py` / `backend/print_predictions_doc.py`
Fixture və proqnoz məlumatlarını çap edən köməkçi skriptlər.
