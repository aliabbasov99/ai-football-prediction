"""
Loqo yükləmə skripti üçün məlumat bazası.

Hər liqa üçün:
  folder  — map_logos.py ilə uyğun qovluq adı ("England - Premier League")
  name    — DB-dəki liqa adı (backend LEAGUE_SLUGS ilə eyni)
  country — TheSportsDB-dəki ölkə adı
  tsdb    — TheSportsDB axtarışında əlavə filtr
  wiki    — Wikipedia səhifə adı (liqa loqosu üçün)
  teams   — komandalar; hər biri ya str, ya (str, [əlavə axtarış adları])

Komanda adları DB-də istifadə olunan qısa/uzun formalara uyğun seçilib
(bax: backend/scripts/map_logos.py ALIASES). Əlavə axtarış adları
TheSportsDB-dəki rəsmi adlardır (məs. "Inter Milan", "Inter", "Internazionale").
"""

LEAGUES = {
    # ── İngiltərə ────────────────────────────────────────────────────────────
    "England - Premier League": {
        "name": "Premier League",
        "country": "England",
        "tsdb": "English Premier League",
        "wiki": ["Premier League", "English football league system"],
        "teams": [
            "Arsenal", "Aston Villa", ("Bournemouth", ["AFC Bournemouth"]),
            "Brentford", ("Brighton", ["Brighton & Hove Albion"]),
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
            ("Leeds United", ["Leeds"]), "Liverpool",
            ("Man City", ["Manchester City"]),
            ("Man Utd", ["Manchester United"]),
            ("Newcastle", ["Newcastle United"]),
            ("Nottingham Forest", ["Nott'm Forest", "Nottingham Forest"]),
            "Sunderland", ("Spurs", ["Tottenham Hotspur", "Tottenham Hotspur"]),
            ("West Ham", ["West Ham United"]),
            ("Wolves", ["Wolverhampton Wanderers"]),
        ],
    },
    "England - Championship": {
        "name": "EFL Championship",
        "country": "England",
        "tsdb": "English Championship",
        "wiki": ["EFL Championship", "Football League Championship"],
        "teams": [
            "Birmingham City", "Blackburn Rovers", "Bristol City",
            "Charlton Athletic", "Coventry City", "Derby County", "Hull City",
            "Ipswich Town", "Leicester City", "Middlesbrough", "Millwall",
            "Norwich City", "Portsmouth", "Queens Park Rangers",
            ("Sheff Utd", ["Sheffield United"]), "Southampton", "Stoke City",
            "Swansea City", "Sheffield Wednesday", "Wigan Athletic",
        ],
    },
    # ── İspaniya ─────────────────────────────────────────────────────────────
    "Spain - LaLiga": {
        "name": "La Liga",
        "country": "Spain",
        "tsdb": "Spanish La Liga",
        "wiki": ["La Liga"],
        "teams": [
            "Alavés", ("Athletic Club", ["Athletic Bilbao"]),
            ("Atletico Madrid", ["Atlético de Madrid"]),
            ("Barcelona", ["FC Barcelona"]),
            "Celta Vigo", "Elche", "Espanyol", "Getafe", "Girona", "Levante",
            "Mallorca", "Osasuna", "Rayo Vallecano", ("Betis", ["Real Betis"]),
            "Real Madrid", "Real Oviedo", "Real Sociedad",
            ("Sevilla", ["Sevilla FC"]), ("Valencia", ["Valencia CF"]),
            ("Villarreal", ["Villarreal CF"]),
        ],
    },
    # ── Almaniya ─────────────────────────────────────────────────────────────
    "Germany - Bundesliga": {
        "name": "Bundesliga",
        "country": "Germany",
        "tsdb": "German Bundesliga",
        "wiki": ["Bundesliga"],
        "teams": [
            "Augsburg", ("Bayer Leverkusen", ["Bayer 04 Leverkusen"]),
            ("Bayern Munich", ["FC Bayern München", "Bayern Munchen"]),
            ("Dortmund", ["Borussia Dortmund"]),
            ("Gladbach", ["Borussia Mönchengladbach", "Borussia Monchengladbach"]),
            ("Frankfurt", ["Eintracht Frankfurt"]),
            ("Freiburg", ["SC Freiburg"]),
            "Heidenheim", "Hoffenheim", "Holstein Kiel", "Köln",
            ("Mainz 05", ["Mainz", "1. FSV Mainz 05"]),
            ("RB Leipzig", ["Leipzig"]),
            "St. Pauli", ("Stuttgart", ["VfB Stuttgart"]),
            ("Union Berlin", ["1. FC Union Berlin"]),
            "Werder Bremen", "Wolfsburg",
        ],
    },
    # ── İtaliya ──────────────────────────────────────────────────────────────
    "Italy - Serie A": {
        "name": "Serie A",
        "country": "Italy",
        "tsdb": "Italian Serie A",
        "wiki": ["Serie A", "Serie A 2025-2026"],
        "teams": [
            "Atalanta", "Bologna", "Cagliari", "Como", "Cremonese",
            ("Fiorentina", ["ACF Fiorentina"]),
            "Genoa", "Hellas Verona", ("Inter", ["Inter Milan", "Internazionale"]),
            "Juventus", "Lazio", "Lecce", ("Milan", ["AC Milan"]),
            ("Napoli", ["SSC Napoli"]), "Parma", "Pisa", ("Roma", ["AS Roma"]),
            "Sassuolo", "Torino", "Udinese",
        ],
    },
    # ── Fransa ───────────────────────────────────────────────────────────────
    "France - Ligue 1": {
        "name": "Ligue 1",
        "country": "France",
        "tsdb": "French Ligue 1",
        "wiki": ["Ligue 1", "Ligue 1 2025-2026"],
        "teams": [
            "Angers", "Auxerre", "Brest", "Le Havre", "Lens",
            ("Lille", ["LOSC Lille"]),
            "Lorient", ("Lyon", ["Olympique Lyonnais"]),
            ("Marseille", ["Olympique de Marseille"]), "Metz",
            ("Monaco", ["AS Monaco"]),
            "Nantes", "Nice", ("Paris SG", ["Paris Saint-Germain", "PSG"]),
            "Paris FC", "Rennes", "Strasbourg", "Toulouse",
        ],
    },
    # ── Niderland ────────────────────────────────────────────────────────────
    "Netherlands - Eredivisie": {
        "name": "Eredivisie",
        "country": "Netherlands",
        "tsdb": "Dutch Eredivisie",
        "wiki": ["Eredivisie"],
        "teams": [
            "Ajax", "Almere City", ("AZ Alkmaar", ["AZ"]), "Excelsior",
            "Feyenoord", "Fortuna Sittard", "Go Ahead Eagles", "Groningen",
            "Heerenveen", "Heracles Almelo", "NAC Breda", "NEC Nijmegen",
            "PEC Zwolle", ("PSV Eindhoven", ["PSV", "PSV Eindhoven"]),
            "Sparta Rotterdam", ("Twente", ["FC Twente"]),
            "Utrecht", "Willem II",
        ],
    },
    # ── Braziliya ────────────────────────────────────────────────────────────
    "Brazil - Serie A": {
        "name": "Brasileirao",
        "country": "Brazil",
        "tsdb": "Brazilian Serie A",
        "wiki": ["Campeonato Brasileiro Série A"],
        "teams": [
            "Atlético Mineiro", "Bahia", "Botafogo", "Ceará",
            "Corinthians", "Cruzeiro", "Flamengo", "Fluminense",
            "Fortaleza", "Grêmio", "Internacional", "Juventude", "Mirassol",
            "Palmeiras", "Red Bull Bragantino", "Santos", "São Paulo",
            "Sport Recife", "Vasco da Gama", "Vitória",
        ],
    },
    # ── Portugal ─────────────────────────────────────────────────────────────
    "Portugal - Liga Portugal": {
        "name": "Primeira Liga",
        "country": "Portugal",
        "tsdb": "Portuguese Liga Portugal",
        "wiki": ["Primeira Liga", "Liga Portugal"],
        "teams": [
            "Arouca", "Benfica", "Boavista", "Braga", "Casa Pia", "Estoril",
            "Estrelas da Amadora", "Farense", "Gil Vicente", "Moreirense",
            "Nacional", "Porto", "Rio Ave", "Santa Clara",
            ("Sporting CP", ["Sporting"]),
            "Tondela", "Vitinha Guimaraes", "AVS",
        ],
    },
    # ── Argentina ────────────────────────────────────────────────────────────
    "Argentina - Primera Division": {
        "name": "Primera Division",
        "country": "Argentina",
        "tsdb": "Argentine Primera Division",
        "wiki": ["Primera División", "Argentine Primera División"],
        "teams": [
            "Aldosivi", "Argentinos Juniors", "Atlético Tucumán", "Banfield",
            "Barracas Central", "Belgrano", "Boca Juniors",
            "Central Córdoba", "Defensa y Justicia", "Deportivo Riestra",
            "Estudiantes", "Gimnasia La Plata", "Godoy Cruz", "Huracán",
            "Independiente", "Independiente Rivadavia", "Instituto", "Lanús",
            "Newell's Old Boys", "Platense", "Racing Club", "River Plate",
            "Rosario Central", "San Lorenzo", "San Martín de San Juan",
            "Talleres", "Tigre", "Unión", "Vélez Sarsfield",
        ],
    },
    # ── Belçika ──────────────────────────────────────────────────────────────
    "Belgium - Jupiler Pro League": {
        "name": "Pro League",
        "country": "Belgium",
        "tsdb": "Belgian First Division A",
        "wiki": [
            "Belgian Division 1",
            "Eerste klasse A 2025-26 (voetbal België)",
            "Belgian Pro League",
            "Belgian First Division A",
        ],
        "teams": [
            "Anderlecht", "Antwerp", "Beerschot", "Cercle Brugge",
            "Charleroi", ("Club Brugge", ["Brugge"]),
            "Dender", "Genk", "Gent", "Kortrijk", "KV Mechelen",
            "OH Leuven", "Sint-Truiden", "Standard Liège",
            "Union Saint-Gilloise", "Westerlo",
        ],
    },
    # ── Türkiyə ──────────────────────────────────────────────────────────────
    "Turkey - Super Lig": {
        "name": "Super Lig",
        "country": "Turkey",
        "tsdb": "Turkish Super Lig",
        "wiki": ["Süper Lig", "Turkish Super Lig"],
        "teams": [
            "Adana Demirspor", "Alanyaspor", "Antalyaspor", "Beşiktaş",
            "Çaykur Rizespor", "Eyüpspor", "Fatih Karagümrük",
            "Fenerbahçe", "Fenerbahce", "Galatasaray", "Gaziantep FK",
            "Göztepe", "Kasımpaşa", "Kayserispor", "Kocaelispor",
            "Samsunspor", "Sivasspor", "Trabzonspor", "Zonguldakspor",
        ],
    },
    # ── Səudiyyə Ərəbistan ───────────────────────────────────────────────────
    "Saudi Arabia - Saudi Pro League": {
        "name": "Saudi Pro League",
        "country": "Saudi Arabia",
        "tsdb": "Saudi Pro League",
        "wiki": ["Saudi Pro League", "Saudi Arabian league"],
        "teams": [
            "Al Ahli", "Al Ettifaq", "Al Fateh", "Al Fayha", "Al Hilal",
            "Al Ittihad", "Al Kholood", "Al Nassr", "Al Okhdood", "Al Orobah",
            "Al Qadsiah", "Al Shabab", "Al Taawoun", "Al Wehda",
            "Al Jeddah", "Damac", "Neom SC", "Riyadh United",
        ],
    },
    # ── ABŞ ──────────────────────────────────────────────────────────────────
    "USA - MLS": {
        "name": "MLS",
        "country": "USA",
        "tsdb": "American Major League Soccer",
        "wiki": ["Major League Soccer"],
        "teams": [
            "Atlanta United", "Austin FC", "Charlotte FC", "Chicago Fire",
            "Colorado Rapids", "Columbus Crew", "D.C. United", "FC Cincinnati",
            "FC Dallas", "Houston Dynamo", "Inter Miami", "LA Galaxy",
            "Los Angeles FC", "Minnesota United", "CF Montréal",
            "Nashville SC", "New England Revolution", "New York City FC",
            "New York Red Bulls", "Philadelphia Union", "Portland Timbers",
            "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders",
            "Sporting Kansas City", "Toronto FC", "Vancouver Whitecaps",
        ],
    },
    # ── Çexiya ───────────────────────────────────────────────────────────────
    "Czech Republic - Chance Liga": {
        "name": "Czech First League",
        "country": "Czech Republic",
        "tsdb": "Czech 1. Liga",
        "wiki": ["Czech First League", "Chance Liga"],
        "teams": [
            "Baník Ostrava", "Bohemians 1905", "Dukla Praha",
            "Hradec Králové", "Jablonec", "Karviná", "Mladá Boleslav",
            "Pardubice", "Příbram", "Sigma Olomouc", "Slavia Praha",
            "Slovan Liberec", "Sparta Praha", "Teplice", "Viktoria Plzeň",
            "Zlín",
        ],
    },
    # ── Yunanıstan ───────────────────────────────────────────────────────────
    "Greece - Super League 1": {
        "name": "Super League Greece",
        "country": "Greece",
        "tsdb": "Greek Super League 1",
        "wiki": ["Super League Greece", "Super League 1"],
        "teams": [
            "AEK Athens", "AEL Larissa", "Aris", "Asteras Tripolis", "Atromitos",
            "Kifisia", "Levadiakos", "OFI Crete", "Olympiacos", "Panathinaikos",
            "Panetolikos", "Panionios", "PAOK", "Volos NFC",
        ],
    },
    # ── Ekvador ──────────────────────────────────────────────────────────────
    "Ecuador - LigaPro": {
        "name": "Liga Pro Ecuador",
        "country": "Ecuador",
        "tsdb": "Ecuadorian Serie A",
        "wiki": ["LigaPro", "Liga Protección", "Ecuadorian Serie A"],
        "teams": [
            "Aucas", "Barcelona SC", "Delfín", "Deportivo Cuenca",
            "El Nacional", "Emelec", "Everest PNG", "Guayas", "IDV",
            "Independiente del Valle", "LDU Quito", "Macará", "Manta",
            "Mushuc Runa", "Orense", "Sociedad Deportivo Quito",
            "Técnico Universitario",
        ],
    },
    # ── Daniya ───────────────────────────────────────────────────────────────
    "Denmark - Superliga": {
        "name": "Danish Superliga",
        "country": "Denmark",
        "tsdb": "Danish Superliga",
        "wiki": ["Danish Superliga", "Danish football league"],
        "teams": [
            "AaB", "AGF", "Brøndby", "Copenhagen",
            ("København", ["FC Copenhagen", "FC København"]),
            "Midtjylland", "Nordsjælland", "OB", "Randers", "Silkeborg",
            "Sønderjyske", "Viborg", "Vejle",
        ],
    },
    # ── Polya ────────────────────────────────────────────────────────────────
    "Poland - PKO BP Ekstraklasa": {
        "name": "Ekstraklasa",
        "country": "Poland",
        "tsdb": "Polish I Liga",
        "wiki": [
            "2025\u201326 Ekstraklasa",
            "Ekstraklasa",
            "I liga (Poland)",
        ],
        "teams": [
            "Arka Gdynia", "Cracovia", "Górnik Zabrze", "Jagiellonia",
            "Korona Kielce", "Lech Poznań", "Lechia Gdańsk", "Legia Warsaw",
            "Motor Lublin", "Piast Gliwice", "Pogoń Szczecin",
            "Radomiak Radom", "Raków Częstochowa", "Stal Mielec",
            "Widzew Łódź", "Wisła Kraków", "Wisła Płock", "Warta Poznań",
            "Zagłębie Lubin",
        ],
    },
    # ── Yaponiya ─────────────────────────────────────────────────────────────
    "Japan - J1 League": {
        "name": "J1 League",
        "country": "Japan",
        "tsdb": "Japanese J1 League",
        "wiki": ["J1 League", "Japan Soccer League"],
        "teams": [
            "Avispa Fukuoka", "Cerezo Osaka", "Fagiano Okayama", "FC Osaka",
            "FC Tokyo", "Gamba Osaka", "Kashima Antlers", "Kashiwa Reysol",
            "Kawasaki Frontale", "Kyoto Sanga", "Machida Zelvia",
            "Nagoya Grampus", "Sanfrecce Hiroshima", "Shimizu S-Pulse",
            "Shonan Bellmare", "Tokyo Verdy", "Urawa Red Diamonds",
            "Vissel Kobe", "Yokohama F. Marinos", "Yokohama FC",
        ],
    },
    # ── Norveç ───────────────────────────────────────────────────────────────
    "Norway - Eliteserien": {
        "name": "Eliteserien",
        "country": "Norway",
        "tsdb": "Norwegian Eliteserien",
        "wiki": ["Eliteserien", "Tippeligaen"],
        "teams": [
            "Brann", "Bodø/Glimt", "Fredrikstad", "HamKam", "Haugesund",
            "KFUM Oslo", "Lillestrøm", "Molde", "Odd", "Rosenborg",
            "Sandefjord", "Sarpsborg 08", "Strømsgodset", "Tromsø",
            "Vålerenga", "Viking",
        ],
    },
    # ── Çin ──────────────────────────────────────────────────────────────────
    "China - Chinese Super League": {
        "name": "Chinese Super League",
        "country": "China",
        "tsdb": "Chinese Super League",
        "wiki": ["Chinese Super League", "Chinese football league"],
        "teams": [
            "Beijing Guoan", "Changchun Yatai", "Chengdu Rongcheng",
            "China Life Hunan", "Henan Songshan Longmen", "Meizhou Hakka",
            "Qingdao West Coast", "Qingdao Hainiu", "Shanghai Port",
            "Shanghai Shenhua", "Shandong Taishan", "Shenzhen Peng City",
            "Suzhou Golden Town", "Tianjin Jinmen Tiger", "Wuhan Three Towns",
            "Zhejiang FC",
        ],
    },
    # ── Estoniya ─────────────────────────────────────────────────────────────
    "Estonia - Meistriliiga": {
        "name": "Meistriliiga",
        "country": "Estonia",
        "tsdb": "Estonian Meistriliiga",
        "wiki": ["Meistriliiga", "Estonian football league"],
        "teams": [
            "Flora", "Harju JK", "FCI Levadia", "JK Tabasalu", "Kalev",
            "Kalju", "Kuressaare", "Narva Trans", "Paide Linna JK",
            "Tartu JK Tammeka", "Viimsi Tervise JK",
        ],
    },
    # ── Belarus ──────────────────────────────────────────────────────────────
    "Belarus - Vysshaya Liga": {
        "name": "Vysheyshaya Liga",
        "country": "Belarus",
        "tsdb": "Belarusian Premier League",
        "wiki": ["Vysshaya Liga", "Belarusian Premier League"],
        "teams": [
            "Arsenal Dzerzhinsk", "BATE", "Dinamo Brest", "Dinamo Minsk",
            "Dnepr Mogilev", "Energetyk-BGU", "Gomel", "Isloch",
            "Krumkachy", "Lokomotiv Vitebsk", "Maxline Vitebsk", "Minsk",
            "Molodechno", "Naftan Novopolotsk", "Novaje Pinsk", "Slavia Mozyr",
            "Sputnik", "Torpedo-BelAZ",
        ],
    },
    # ── Azərbaycan ───────────────────────────────────────────────────────────
    "Azerbaijan - Premier League": {
        "name": "Super Liqa",
        "country": "Azerbaijan",
        "tsdb": "Azerbaijani Premier League",
        "wiki": ["Azerbaijan Premier League", "Azerbaijani football league"],
        "teams": [
            "Qarabag", "Neftçi", "Sabah", "Qayalag Zirə", "Zira",
            "Turan Tovuz", "Inter Baku", "Sabail", "Gabala", "Ağdam",
            "Sumgayit", "Kapaz",
        ],
    },
}

# slug -> (folder, wiki) — frontend-in LEAGUE_LOGO_FALLBACK ilə eyni açar dəyərləri
LEAGUE_SLUG_LOOKUP = {
    "premier_league": "England - Premier League",
    "laliga": "Spain - LaLiga",
    "bundesliga": "Germany - Bundesliga",
    "serie-a": "Italy - Serie A",
    "ligue-1": "France - Ligue 1",
    "eredivisie": "Netherlands - Eredivisie",
    "brasileirao": "Brazil - Serie A",
    "primeira-liga": "Portugal - Liga Portugal",
    "primera-division": "Argentina - Primera Division",
    "belgian-pro-league": "Belgium - Jupiler Pro League",
    "super-lig": "Turkey - Super Lig",
    "efl-championship": "England - Championship",
    "saudi-pro-league": "Saudi Arabia - Saudi Pro League",
    "mls": "USA - MLS",
    "czech-first-league": "Czech Republic - Chance Liga",
    "super-league-greece": "Greece - Super League 1",
    "liga-pro-ecuador": "Ecuador - LigaPro",
    "danish-superliga": "Denmark - Superliga",
    "ekstraklasa": "Poland - PKO BP Ekstraklasa",
    "j1-league": "Japan - J1 League",
    "eliteserien": "Norway - Eliteserien",
    "chinese-super-league": "China - Chinese Super League",
    "meistriliiga": "Estonia - Meistriliiga",
    "vysheyshaya-liga": "Belarus - Vysshaya Liga",
    "super-liqa": "Azerbaijan - Premier League",
}

# LEAGUE_SLUGS (backend) -> slug
BACKEND_SLUG_TO_FILE = {
    "PL": "premier_league",
    "LaLiga": "laliga",
    "BL": "bundesliga",
    "SA": "serie-a",
    "L1": "ligue-1",
    "ED": "eredivisie",
    "Brasileirao": "brasileirao",
    "PrimL": "primeira-liga",
    "PriD": "primera-division",
    "ProL": "belgian-pro-league",
    "SL": "super-lig",
    "EFL": "efl-championship",
    "SPL": "saudi-pro-league",
    "MLS": "mls",
    "CFL": "czech-first-league",
    "SLG": "super-league-greece",
    "LPE": "liga-pro-ecuador",
    "DSL": "danish-superliga",
    "EKS": "ekstraklasa",
    "J1L": "j1-league",
    "ELI": "eliteserien",
    "CSL": "chinese-super-league",
    "ML": "meistriliiga",
    "VL": "vysheyshaya-liga",
    "SLQ": "super-liqa",
}


def expand(entry):
    """'X' -> ('X', []);  ('X', [aliases]) -> ('X', aliases)"""
    if isinstance(entry, tuple):
        return entry[0], list(entry[1])
    return entry, []
