<div align="center">

<img src="assets/banner.svg" alt="BookBridge" width="100%"/>

### 📚 A community platform where books circulate instead of gathering dust

[![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/bookbridge/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white)](https://github.com/YOUR_USERNAME/bookbridge/actions)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/bookbridge?color=blue)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/bookbridge?color=orange)](https://github.com/YOUR_USERNAME/bookbridge/commits/main)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/bookbridge?style=social)](https://github.com/YOUR_USERNAME/bookbridge)

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white)

</div>

---

## ✨ What is BookBridge?

BookBridge helps people **lend, borrow, exchange and donate physical books** within trusted local communities.
It is **not a marketplace**: no money changes hands for books. Think *Airbnb's trust model + Goodreads' reading identity + Discord's community.*

> 🎯 **Vision:** India's largest community-driven book-sharing network.

## 🚀 Features

| | Feature | Highlights |
|---|---|---|
| 🔎 | **Smart search** | Title, author, ISBN, genre, language, college, city. Distance and condition filters |
| 🤝 | **Exchange workflow** | Request → accept → pickup → borrow → return → review, with reminders |
| 💬 | **Gated chat** | Chat opens only after an exchange exists. Text, images, read receipts |
| 🛡️ | **Trust score** | Based on returns, reviews, cancellations and response time |
| 📖 | **Book Journey** | Every physical copy keeps its own history, quotes and lessons |
| ⭐ | **Wishlist alerts** | Get notified when a wanted book becomes available |
| 👥 | **Reading clubs** | Schedules, polls, discussions, events |
| 📊 | **Impact dashboard** | Books read, money saved, CO₂ avoided, reading streak |

## 🏗️ Architecture

```mermaid
flowchart LR
  U([Users]) --> CF[CloudFront + WAF]
  CF --> WEB[React SPA on S3]
  CF --> ALB[Load Balancer]
  ALB --> API[FastAPI modular monolith]
  ALB --> RT[Realtime gateway]
  API --> PG[(PostgreSQL)]
  API --> R[(Redis)]
  API --> OUT[Outbox] --> Q[SNS / SQS] --> W[Workers]
  W --> PG
  W --> N[Email / Push]
  API --> CL[Cloudinary]
```

**Key ideas:** modular monolith with event-driven boundaries · Postgres as the source of truth · transactional outbox · cursor pagination · idempotent APIs · infrastructure as code.

## ⚡ Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/bookbridge.git
cd bookbridge
cp .env.example .env          # add your local values
docker compose up --build     # api, worker, postgres, redis
```

| Service | URL |
|---|---|
| Web app | http://localhost:5173 |
| API docs (Swagger) | http://localhost:8000/docs |

> 📝 Commands assume the repo layout described in the docs. Adjust to your setup.

## 🗂️ Project Structure

```text
bookbridge/
├── backend/    # FastAPI: modules/ (identity, catalog, exchange, chat…), core/, tasks/
├── web/        # React + TS + Tailwind: features/, shared/, app/
├── infra/      # Terraform: network, ecs, rds, redis, monitoring
├── docs/       # PRD, HLD, DB schema, API spec, deployment
└── .github/    # CI/CD workflows
```

## 📚 Documentation

| Doc | Description |
|---|---|
| 📄 PRD | Vision, personas, requirements, roadmap |
| 🧭 High Level Design | Components, data flow, request flows |
| 🗄️ Database Schema | 66 tables with ER diagrams |
| 🔌 REST API | ~135 endpoints, errors, pagination |
| 🎨 Frontend Architecture | Routing, state, auth, wireframes |
| ☁️ Deployment | AWS, Docker, CI/CD, DR, cost |

## 🗺️ Roadmap

- [x] Product requirements and architecture
- [ ] **MVP:** auth, listings, search, exchange workflow, chat, notifications, trust v1
- [ ] Reading clubs and Book Journey
- [ ] Semantic search and recommendations
- [ ] Barcode scan, QR pickup, mobile app
- [ ] Graph-based chain exchanges (A → B → C)

## 🤝 Contributing

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Run `make lint test` before committing
3. Open a pull request with a clear description

## 📜 License

Released under the [MIT License](LICENSE).

<div align="center">

**Made with ❤️ for readers everywhere** · ⭐ Star the repo if you like the idea

</div>
