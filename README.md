# Outfit Atelier - Style Checker

A simple web app that helps people who are not sure about fashion. Point your
camera, press one button, and get plain-language feedback: do your top and
bottom match, is the colour good for your skin tone, and which accessories and
shoes go with it.

Built for people who have never had anyone to ask "does this look okay?"

**Live demo:** _add your link here after deploying_

## What it does

- **Colour match:** finds the main colour of your top and bottom and tells you, in everyday colour names (navy, mustard, beige...), if they go well together.
- **Skin-tone advice:** tells you whether the top colour suits your skin tone near the face. *You pick your skin tone from a menu. It is never guessed from your face.*
- **Other colours that go with it:** if the match is weak, it suggests bottoms to keep your top (or tops to keep your bottom).
- **Accessories and shoes:** suggestions based on your outfit colours and where you are going (casual, office, formal, evening, festival).
- **Style tips** for a goal you choose (structure, balance, elongate, relaxed).
- **Login:** accounts with bcrypt-hashed passwords and JWT tokens. Each user sees only their own history.
- **History** of past checks.

**By design, the app does not:**
- run automatically or watch you. Nothing happens until you press "Check my outfit"
- analyse your body shape, weight, size or face
- save your photo. Only the colour values are stored

## Tech stack

| Part | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Auth | bcrypt (password hashing), PyJWT (login tokens) |
| MySQL / SQLite | users, preferences, outfit-check history (SQLAlchemy) |
| MongoDB | style-tips library, detailed analysis logs |
| Tests | pytest, FastAPI TestClient, GitHub Actions |

## How it works

1. The browser shows the camera with two guide boxes (top and bottom).
2. When you press the button, React sends one small photo to `POST /api/analyze` with your login token.
3. FastAPI checks the token, decodes the photo and crops the two boxes.
4. `color_utils.py` reduces each box to a few colours, picks the main one, converts it to HSV and names it.
5. Colour-wheel rules (neutral, tonal, complementary, clashing) give a score and a verdict.
6. `advice.py` turns the colours plus your skin tone and occasion into suggestions. Everything is a visible rule, not a black box.
7. The full detail goes to MongoDB, a summary row goes to MySQL, and the result goes back to the screen.

```
outfit-style-checker/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app; also serves the built website
│   │   ├── config.py          # settings from environment variables
│   │   ├── security.py        # bcrypt hashing + JWT login tokens
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── mongo.py           # MongoDB client (or mongomock for easy dev)
│   │   ├── models.py          # User, Preference, OutfitCheck tables
│   │   ├── schemas.py         # request/response validation
│   │   ├── color_utils.py     # dominant colour, colour names, harmony score
│   │   ├── advice.py          # skin-tone, accessory, shoe and colour-pairing rules
│   │   ├── seed_tips.py       # style tips for MongoDB
│   │   └── routers/           # auth, preferences, tips, analyze, history
│   ├── tests/                 # pytest tests
│   └── requirements.txt
├── frontend/                  # React app (builds into backend/app/static)
├── docker-compose.yml         # real MySQL + MongoDB (optional)
└── .github/workflows/tests.yml
```

## Run it on your computer

You need Python 3.12 and Node.js. No database installs are needed: it uses SQLite and an in-memory MongoDB stand-in by default.

**Backend** (terminal 1):
```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate      Mac/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend** (terminal 2):
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173, create an account and allow the camera.

## Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```
The tests cover the colour rules, the advice rules, password hashing, login, token protection, per-user privacy and the full analyse flow.

## Build the website for production

```bash
cd frontend
npm install
npm run build        # writes the site into backend/app/static
```
After this, the backend alone serves both the website and the API from one address. Commit the `backend/app/static` folder so the deploy needs no Node.js.

## Deploy (Render, free plan)

1. Push this project to GitHub (with `backend/app/static` included).
2. On render.com create a **New Web Service** and pick this repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Language:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free
4. Environment variables:
   - `PYTHON_VERSION` = `3.12.3`
   - `JWT_SECRET` = a long random value (use Render's Generate button)
5. Deploy. The camera needs HTTPS, which Render provides.

> On the free plan the disk is temporary, so accounts and history reset when the service restarts, and the first visit after a quiet period can take about a minute. For permanent data use real MySQL and MongoDB (see below).

## Use real MySQL and MongoDB

```bash
docker compose up -d
```
Then set these in `backend/.env`:
```
DATABASE_URL=mysql+pymysql://outfit_user:outfit_pass@localhost:3306/outfit_checker
USE_MONGOMOCK=false
MONGO_URI=mongodb://localhost:27017
```

## API

| Method | Path | Login needed | Description |
|---|---|---|---|
| GET | `/api/health` | no | Health check |
| POST | `/api/auth/register` | no | Create account, returns a token |
| POST | `/api/auth/login` | no | Log in, returns a token |
| GET | `/api/auth/me` | yes | Current user |
| GET / PUT | `/api/preferences` | yes | Skin tone, occasion, style goal |
| GET | `/api/tips?goal=...` | no | Style tips for a goal |
| POST | `/api/analyze` | yes | Check an outfit from a photo |
| GET | `/api/history` | yes | Your past checks |

Interactive API docs are available at `/docs` when the server is running.

## Security notes

- Passwords are hashed with bcrypt and never stored or returned as plain text.
- Login tokens (JWT) expire after 7 days and are signed with `JWT_SECRET`. Always set your own secret in production.
- Wrong username and wrong password give the same error message.
- Every user can read only their own preferences and history.

## Ideas for next steps

- Hindi and Kannada language support
- Gender-specific outfit and accessory suggestions
- Save favourite outfits and compare checks over time
- Use a real MySQL/MongoDB host so accounts survive restarts

## Author

Darshini B - [GitHub](https://github.com/darshinibharadhwaj) | [LinkedIn](https://www.linkedin.com/in/darshinia156942a3)
