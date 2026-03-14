# Museum AI Backend (MERN)

Node.js + Express + MongoDB API for the Museum AI platform.

## Prerequisites

- **Node.js** 18+
- **MongoDB** running locally (`mongodb://127.0.0.1:27017`) or set `MONGODB_URI` in `.env`

## Setup

```bash
cd backend
npm install
cp .env.example .env   # optional; defaults work for local dev
```

## Run

```bash
npm run dev    # development with auto-reload
# or
npm start      # production
```

Server runs at **http://localhost:5000**.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | API status |
| GET | `/api/health/db` | MongoDB connection status |
| POST | `/api/contact` | Contact form (name, email, subject?, message) |

## Environment

- `PORT` — default 5000
- `MONGODB_URI` — default `mongodb://127.0.0.1:27017/museum-ai`
