# Outfit Atelier — Style Checker

An on-demand color-coordination checker: point your webcam, click a button when
you're ready, and get feedback on how your top and bottom pair together — plus
style tips matched to a goal you choose yourself.

**By design, this app does not:**
- run automatically or watch you passively — nothing happens until you click "Check my outfit"
- analyze your body shape, weight, or size
- give weight-loss/weight-gain advice

**What it does do:**
- extracts the dominant color from a top region and a bottom region you align yourself
- scores the pairing using standard color-wheel rules (analogous, complementary, neutral, clashing)
- shows style tips (structure / balance / elongate / relaxed — cuts, layering, proportion) matched to a goal you pick from a menu, never inferred from your photo
- keeps a history of your past checks

## Stack

- **Frontend:** React + TypeScript (Vite), Tailwind CSS
- **Backend:** Python, FastAPI
- **MySQL:** structured data — users, style preferences, outfit-check history
- **MongoDB:** flexible data — the style-tips library, detailed per-check analysis logs

## Project structure

```
outfit-style-checker/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entrypoint
│   │   ├── config.py          # env-based settings (DB URLs, mongomock toggle)
│   │   ├── database.py        # SQLAlchemy engine/session (MySQL or SQLite)
│   │   ├── mongo.py           # pymongo client (or mongomock for zero-setup dev)
│   │   ├── models.py          # User, Preference, OutfitCheck (SQL tables)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── color_utils.py     # dominant-color extraction + harmony scoring
│   │   ├── seed_tips.py       # seeds the MongoDB style-tips collection
│   │   └── routers/           # users, preferences, tips, analyze, history
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   └── components/        # WebcamPanel, ResultCard, GoalPicker, History
│   └── package.json
├── docker-compose.yml          # real MySQL + MongoDB for production-style local run
└── README.md
```

## Running it — Quick start (no database installs needed)

The backend defaults to SQLite + an in-memory Mongo stand-in (`mongomock`), so
you can run the whole thing with nothing but Python and Node installed.

**Backend:**
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
The API is now at `http://localhost:8000`. Tips are seeded automatically on first run.

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open `http://localhost:5173`. Your browser will ask for camera permission — allow it, then click "Check my outfit" to run a check.

## Running it with real MySQL + MongoDB

```bash
docker compose up -d
```

This starts MySQL on `localhost:3306` and MongoDB on `localhost:27017` (credentials in `docker-compose.yml`). Then edit `backend/.env`:

```
DATABASE_URL=mysql+pymysql://outfit_user:outfit_pass@localhost:3306/outfit_checker
USE_MONGOMOCK=false
MONGO_URI=mongodb://localhost:27017
```

Restart the backend (`uvicorn app.main:app --reload --port 8000`) — it will create the MySQL tables automatically and seed the Mongo tips collection on first boot.

## API reference

| Method | Path                          | Description                                  |
|--------|-------------------------------|------------------------------------------------|
| GET    | `/api/health`                 | Health check                                    |
| POST   | `/api/users`                  | Create a user profile (`display_name`)          |
| GET    | `/api/users/{id}`              | Get a user                                      |
| GET    | `/api/users/{id}/preferences`  | Get style preferences                           |
| PUT    | `/api/users/{id}/preferences`  | Update style goal / occasion / favorite colors  |
| GET    | `/api/tips?goal=...`           | Get tips for a style goal                       |
| POST   | `/api/analyze`                | Analyze a captured frame (see below)            |
| GET    | `/api/history/{user_id}`       | Past outfit checks                              |

`POST /api/analyze` body:
```json
{
  "user_id": 1,
  "image_base64": "data:image/jpeg;base64,...",
  "top_box": [0.28, 0.16, 0.72, 0.42],
  "bottom_box": [0.28, 0.52, 0.72, 0.85]
}
```
`top_box`/`bottom_box` are fractional crop regions (left, top, right, bottom, each 0–1) — these match the guide boxes drawn over the webcam preview in the frontend.

## How the color engine works

`backend/app/color_utils.py` crops the two regions you aligned, quantizes each
to a small palette, and picks the most common non-background color. It then
converts both colors to HSV and applies color-wheel rules:
- either color being a neutral (black/white/grey/navy/beige) → always a safe pairing
- hue difference under 40° → harmonious/tonal
- hue difference 150–210° → bold complementary contrast
- everything else → flagged as a closer look, with a suggestion (add a neutral layer, adjust shade, etc.)

This is intentionally a transparent, rule-based system — not a black-box model — so the reasoning behind every verdict is inspectable in that one file.

## Pushing this to GitHub

Same steps as your last project:

```bash
git add .
git commit -m "Initial commit: outfit style checker"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

(Create the empty repo first at github.com/new, without a README, to avoid a merge conflict — and make sure you're signed into the correct GitHub account before pushing.)
