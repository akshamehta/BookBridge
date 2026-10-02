# BookBridge — Product Requirements Document

|  |  |
| --- | --- |
| **Status** | Draft v1.0 for review |
| **Owner** | Product (PM) · Eng Lead (SDE) |
| **Last updated** | 1 Oct 2026 |
| **Launch market** | India (Tier-1 college cities first) |

---

## 1. Vision

Build India's largest community-driven book-sharing network, where books circulate among readers instead of sitting unused on shelves.

**One-line positioning:** *Airbnb's trust model + Goodreads' reading identity + Discord's community, for physical books.*

BookBridge is **not a marketplace**. No money changes hands for books. Value is measured in books circulated, readers connected and waste avoided, not GMV.

## 2. Problem Statement

1. **Access gap.** Textbooks and novels are expensive relative to student budgets. A single semester's books can cost ₹5,000–15,000, and most are read once.
2. **Idle supply.** Households, hostels and alumni hold large numbers of unread or finished books with no easy way to pass them on.
3. **Trust gap.** People hesitate to lend to strangers (loss, damage, no return) and hesitate to meet strangers (safety).
4. **Fragmented coordination.** Sharing today happens through WhatsApp groups, Facebook groups and notice boards: unsearchable, no status tracking, no accountability.
5. **No continuity.** A physical book's journey across readers is lost. Nobody knows where it has been or what it meant to previous readers.

## 3. Existing Solutions

| Category | Examples | What they do |
| --- | --- | --- |
| Social reading | Goodreads, StoryGraph | Track, rate and discover books (digital only) |
| Resale marketplaces | OLX, Amazon Used, Facebook Marketplace, Bookchor | Peer or business used-book sales |
| Rental/subscription | Rentomojo-style book rental, Kindle Unlimited | Paid access |
| Physical libraries | Public, college and private libraries | Free but limited catalogue and hours |
| Book swap | BookCrossing, Little Free Libraries | Free exchange, mostly offline |
| Ad-hoc communities | WhatsApp, Telegram, college groups | Informal lending |

## 4. Why Existing Solutions Fail

| Gap | Impact |
| --- | --- |
| Goodreads has no physical-copy concept | Cannot answer "who near me has this book?" |
| Marketplaces are transactional and price-driven | Excludes donation/lending; scams; no reputation tied to returns |
| Libraries have fixed catalogues and low discoverability | Students cannot find niche or latest titles |
| BookCrossing has weak product depth | No search, no workflow, no reminders |
| WhatsApp/Facebook groups are unstructured | No availability state, no trust signal, spam, no history |
| None track **copy-level history** | No emotional or trust capital for sharing |

**Insight:** the unsolved problem is not "find a book", it is **"trust a stranger with my book."** BookBridge treats trust, workflow accountability and community as the core product.

## 5. Goals

| # | Goal | Measure |
| --- | --- | --- |
| G1 | Make borrowing a book near me as easy as ordering food | Search-to-request under 2 minutes |
| G2 | Make lending feel safe | Return rate ≥ 90% |
| G3 | Build repeat community behaviour | Month-3 retention ≥ 30% |
| G4 | Create network density in each launch city | ≥ 5,000 listed books per launch campus cluster |
| G5 | Make impact visible | Dashboards for money saved and CO₂ avoided |
| G6 | Safe, spam-free platform | Report-to-resolution under 24 hours |

## 6. Non-Goals

- Selling books, commissions, escrow or payments for books (v1)
- Being an e-book or audiobook reader
- Replacing Goodreads' review and social-graph scale
- Operating logistics or courier delivery (v1; peer pickup only)
- Acting as an official library management system (integration only, later)
- Supporting users under 13 (minimum age 16 for v1 due to DPDP Act 2023 parental-consent complexity)

## 7. User Personas

| Persona | Profile | Needs | Pain points |
| --- | --- | --- | --- |
| **Aarav, 20, Engineering student** | Tier-2 city, tight budget | Free textbooks, previous-year editions | Expensive books, seniors' books wasted |
| **Meera, 34, Professional** | Avid reader, 300+ books | Declutter, meet readers, find niche titles | Books gather dust, no one to discuss with |
| **Kabir, 22, Book-club organiser** | Runs a campus club of 40 | Schedules, polls, shared reading | Coordination across WhatsApp |
| **Priya, NGO coordinator** | Runs donation drives | Collect and distribute bulk books | Manual tracking, no impact data |
| **Dr. Rao, University librarian** | Manages 50k-book library | Extend reach, reduce duplicate stock | No digital lending beyond campus |
| **Admin / Moderator** | Trust and safety | Fast triage of reports and spam | Fake accounts, abuse |

## 8. User Stories

**Auth and profile**

- As a new user, I can sign up with email or Google so that I can start in under a minute.
- As a user, I can reset my password so that I regain access securely.
- As a user, I can set city, college and genres so that I see relevant books.

**Listing**

- As an owner, I can add a book via ISBN lookup and photos so that listing takes under 60 seconds.
- As an owner, I can choose Lend / Exchange / Donate and mark availability so that requests match my intent.

**Discovery**

- As a borrower, I can search by title, author, ISBN, genre, language, city or college and filter by distance, condition and exchange type so that I find the nearest suitable copy.
- As a reader, I can wishlist a book and be notified when a copy becomes available.

**Exchange**

- As a borrower, I request a book with a proposed duration, and the owner can accept or reject.
- As both parties, we finalise pickup time and place, confirm handover and confirm return so that the state is unambiguous.
- As an owner, I get return reminders sent on my behalf so that I do not chase people.

**Chat**

- As a participant in an active request, I can chat (text, images, read receipts) so that I can coordinate. Non-participants cannot message me.

**Trust**

- As a user, I can view another user's trust score and its breakdown before accepting a request.
- As a user, I can review the book, the exchange and the person afterwards.

**Community**

- As a club admin, I can create a club, schedule reading, run polls, host discussions and events.

**Book Journey**

- As a reader, I add a favourite quote and lessons learned so that the next reader sees my note in this copy's timeline.

**Admin**

- As a moderator, I can review reports, ban or suspend users, remove listings and see spam signals.

## 9. Functional Requirements

Priority: **P0** = MVP launch blocker, **P1** = fast-follow, **P2** = later.

### 9.1 Authentication and Account

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-A1 | Email registration with verification link | P0 |
| FR-A2 | Login issuing short-lived JWT access token (15 min) and rotating refresh token | P0 |
| FR-A3 | Google OAuth 2.0 sign-in with account linking | P0 |
| FR-A4 | Forgot/reset password via expiring single-use token | P0 |
| FR-A5 | Profile: name, bio, picture, city, college, interests, favourite genres | P0 |
| FR-A6 | Role-based access: User, Club Admin, Moderator, Admin, Organisation (NGO/Library) | P0 |
| FR-A7 | Account deletion and data export (DPDP compliance) | P1 |
| FR-A8 | College email verification badge | P1 |

### 9.2 Book Management

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-B1 | CRUD for listings with metadata: title, author, ISBN, publisher, language, edition, genre, description, condition, exchange type | P0 |
| FR-B2 | Multiple image upload (max 6) with client-side compression, server-side validation and CDN delivery | P0 |
| FR-B3 | ISBN auto-fill via external metadata API with cache | P1 |
| FR-B4 | Status lifecycle: Available → Reserved → Borrowed → (Available / Exchanged / Donated) | P0 |
| FR-B5 | Soft delete; listings with open requests cannot be deleted | P0 |
| FR-B6 | Bulk upload (CSV) for NGOs and libraries | P2 |
| FR-B7 | Barcode scan and OCR for listing | P2 |

### 9.3 Search and Discovery

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-S1 | Keyword search over title, author, ISBN, genre, language, college, city | P0 |
| FR-S2 | Filters: distance, condition, availability, exchange type | P0 |
| FR-S3 | Typo tolerance, ranking by relevance, distance and owner trust | P0 |
| FR-S4 | Cursor-based pagination | P0 |
| FR-S5 | Semantic search and recommendations using embeddings | P2 |

### 9.4 Exchange Workflow

State machine: `REQUESTED → ACCEPTED → PICKUP_SCHEDULED → BORROWED → RETURN_PENDING → RETURNED → COMPLETED`, with terminal branches `REJECTED`, `CANCELLED`, `EXPIRED`, `DISPUTED`.

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-E1 | Borrower creates request with duration; owner has 72h to respond before auto-expiry | P0 |
| FR-E2 | Accepting reserves the book and auto-declines or queues competing requests | P0 |
| FR-E3 | Pickup details (time, public place suggestions) agreed in-app | P0 |
| FR-E4 | Dual confirmation of handover and of return | P0 |
| FR-E5 | Automated return reminders (T-3 days, T-1 day, due date, overdue) | P0 |
| FR-E6 | Dispute flow (not returned, damaged) escalating to moderators | P1 |
| FR-E7 | Due-date extension requests | P1 |
| FR-E8 | QR-code handover confirmation | P2 |
| FR-E9 | Multi-party chain exchange matching (A→B→C) | P2 |

All transitions are idempotent, audited and validated server-side.

### 9.5 Chat

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-C1 | Conversation is created only when an exchange request exists; closes N days after completion | P0 |
| FR-C2 | Text and image messages, delivery and read receipts | P0 |
| FR-C3 | Block and report within chat; profanity and phone-number-sharing nudges | P1 |
| FR-C4 | Real-time via WebSockets (P0 may ship with short polling) | P1 |

### 9.6 Notifications

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-N1 | Events: request received, accepted, rejected, wishlist fulfilled, return reminder, chat message, club update | P0 |
| FR-N2 | Channels: in-app and email (P0); web/mobile push (P1) | P0/P1 |
| FR-N3 | User preferences, batching and quiet hours | P1 |

### 9.7 Reviews and Trust Score

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-R1 | Reviews for book, exchange experience and user; only after a COMPLETED exchange; one per party per exchange | P0 |
| FR-R2 | Trust score (0–100) from successful exchanges, review rating, on-time returns, cancellation rate and response time, with time decay | P0 |
| FR-R3 | Score breakdown visible to users; new-user baseline with "New member" label | P0 |
| FR-R4 | Abuse resistance: weighted by reviewer trust, collusion detection | P1 |
| FR-R5 | Trust thresholds gate actions (e.g. low score cannot request high-demand books) | P1 |

### 9.8 Wishlist

- FR-W1 (P0): Add/remove wishlist items by title, author or ISBN.
- FR-W2 (P0): Match against new/available listings within the user's radius and notify.
- FR-W3 (P1): Priority queue so the earliest wishlister is offered first.

### 9.9 Reading Clubs

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-K1 | Create public or private clubs; join, leave, invite | P1 |
| FR-K2 | Reading schedule with milestones | P1 |
| FR-K3 | Polls, discussion threads, events with RSVP | P1 |
| FR-K4 | Club roles (owner, moderator, member); club notifications | P1 |

### 9.10 Book Journey

- FR-J1 (P1): Each physical copy has a persistent ID. Every hand-over appends a journey entry: owner, borrow date, return date, review, favourite quote, lessons learned.
- FR-J2 (P1): Public timeline page per copy; shareable.
- FR-J3 (P2): QR sticker on the physical book linking to its journey.

### 9.11 Analytics Dashboard

Books read, borrowed, lent; reading streak; money saved (based on list price); environmental impact (estimated CO₂ and paper saved, methodology documented); favourite genres. (P1)

### 9.12 Admin and Moderation

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-M1 | User management: search, suspend, ban, role change | P0 |
| FR-M2 | Listing management and takedown | P0 |
| FR-M3 | Report queue with SLA tracking | P0 |
| FR-M4 | Spam detection (rate heuristics, duplicate listings, link patterns) | P1 |
| FR-M5 | Audit log of all admin actions | P0 |
| FR-M6 | Admin analytics (growth, exchange funnel, report volume) | P1 |

## 10. Non-Functional Requirements

| Area | Requirement |
| --- | --- |
| **Scalability** | Stateless services, horizontally scalable; target 1M registered users, 100k DAU, 1M listings within 24 months |
| **Latency** | Search p95 \< 300 ms; read APIs p95 \< 200 ms; write APIs p95 \< 500 ms |
| **Availability** | 99.9% for core APIs; graceful degradation (chat or search can fail without blocking exchanges) |
| **Fault tolerance** | Retries with backoff, idempotency keys, circuit breakers, dead-letter queues for jobs |
| **Security** | OWASP Top 10 mitigations, bcrypt/argon2 hashing, JWT rotation and revocation, RBAC, input validation, signed upload URLs, secrets in a manager, TLS everywhere |
| **Privacy** | DPDP Act 2023 compliance: consent, purpose limitation, deletion, export. Exact addresses never shown; approximate location only |
| **Architecture** | Modular monolith with clear bounded contexts (Auth, Catalog, Search, Exchange, Chat, Notification, Trust, Clubs, Admin) and event-driven boundaries so modules can be extracted into services |
| **Data** | PostgreSQL (PostGIS for geo queries, partitioning for messages and events), Redis for cache, rate limits and sessions, search index for low-latency search |
| **Caching** | Cache-aside for hot reads; explicit invalidation on status change |
| **Rate limiting** | Per-IP and per-user token bucket; stricter on auth, requests and messaging |
| **API** | Versioned REST (`/v1`), OpenAPI spec, consistent error schema, cursor pagination |
| **Async** | Background workers for notifications, reminders, image processing, trust-score recalculation, wishlist matching; outbox pattern for reliable event publishing |
| **Observability** | Structured JSON logs with correlation IDs, metrics (RED/USE), distributed tracing, dashboards and alerting on SLOs |
| **Config** | 12-factor, centralised config and feature flags |
| **Deployment** | Docker, AWS (ECS/EKS, RDS, ElastiCache, S3/Cloudinary + CDN), IaC, blue/green or rolling releases |
| **CI/CD** | Lint, type-check, unit and integration tests, container scan, automated migrations, staging gate. Coverage target ≥ 80% on core modules |
| **Accessibility and i18n** | WCAG 2.1 AA; English at launch, Hindi next; i18n-ready strings |
| **Compliance** | Data backups (RPO ≤ 15 min, RTO ≤ 1 h), audit trails, retention policy |

## 11. MVP Scope

**Hypothesis:** if students in one city can find a nearby book and complete a safe borrow-and-return in under a week, they will return and invite others.

**In MVP (P0):** auth (email + Google), profiles, listing with images, search with filters and geo-distance, full exchange workflow with reminders, request-gated chat (text, images, read receipts), in-app and email notifications, wishlist matching, reviews, v1 trust score, basic admin and moderation, rate limiting, logging and monitoring, Dockerised deployment with CI/CD.

**Deliberately out of MVP:** clubs, Book Journey, full analytics, semantic search, push notifications, QR, barcode/OCR, chain matching, mobile app, organisation features.

**Launch plan:** closed beta at 2–3 campuses in one city, seeded by 50–100 power lenders.

## 12. Future Scope

| Theme | Items |
| --- | --- |
| **Community** | Reading clubs, polls, events, NGO donation drives |
| **Intelligence** | Semantic search, AI recommendations, recommendation engine, condition prediction from photos |
| **Graph** | A→B→C exchange matching modelled as a cycle-finding problem on a wishlist/availability graph |
| **Capture** | Barcode scanner, image OCR for auto-listing |
| **Physical** | QR pickup and QR book stickers for journeys |
| **Platform** | React Native app, push notifications, real-time chat at scale |
| **Institutions** | College library integration, bulk onboarding, organisation dashboards |
| **Service split** | Extract Search, Chat and Notifications into independent services |

## 13. Success Metrics

**North Star:** *Successful exchanges completed per week* (request → returned or donated).

| Category | Metric | 6-month target |
| --- | --- | --- |
| Acquisition | Registered users | 25,000 |
| Supply | Books listed | 40,000 |
| Activation | % new users who list or request within 7 days | ≥ 40% |
| Marketplace health | Request acceptance rate | ≥ 60% |
|  | Median time to first response | \< 6 hours |
|  | Search-to-request conversion | ≥ 8% |
| Outcome | Return rate on loans | ≥ 90% |
|  | Completed exchanges / week | 3,000 |
| Retention | D30 / M3 retention | 25% / 30% |
| Trust and safety | Reports per 1,000 exchanges | \< 5 |
|  | Report resolution time | \< 24 h |
| Quality | Avg exchange rating | ≥ 4.5 / 5 |
| Impact | Money saved, kg CO₂ avoided | Reported monthly |
| Engineering | Search p95 latency, API error rate, uptime | \< 300 ms, \< 0.5%, 99.9% |

Guardrails: lost/unreturned books, harassment reports and spam rate must not rise as volume grows.

## 14. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| **Cold start**: no books, no borrowers | High | High | Hyper-local launch, campus ambassadors, seed supply, NGO partnerships |
| **Books not returned** | Medium | High | Trust score gating, reminders, dispute flow, public-place pickup, lend-only-to-verified rules |
| **Safety at meetups** | Medium | High | Public pickup suggestions, college verification, report/block, no exact addresses |
| **Fake reviews and collusion** | Medium | Medium | Review only after completed exchange, weighted scores, anomaly detection |
| **Spam and scams** | High | Medium | Rate limits, listing heuristics, email verification, moderation tooling |
| **Low supply liquidity per area** | High | High | Geo-radius expansion, wishlists, chain matching later |
| **Legal/privacy (DPDP)** | Low | High | Consent flows, data minimisation, deletion and export |
| **Copyright issues with images/metadata** | Low | Medium | User-owned photos only, licensed ISBN APIs |
| **Premature microservices complexity** | Medium | Medium | Modular monolith first, event-driven boundaries |
| **Third-party dependency (Cloudinary, email, OAuth)** | Medium | Medium | Abstraction layers, retries, fallback providers |
| **Infra cost growth** | Medium | Medium | Autoscaling limits, image optimisation, cost dashboards |

## 15. Assumptions

- Readers will lend to strangers if they can see trust history and the borrower's college/city.
- Students have smartphones and are comfortable with email/Google sign-in.
- Hyper-local density (campus or neighbourhood) matters more than national reach.
- Peer pickup in public places is acceptable; no delivery needed in v1.
- ISBN metadata providers cover most Indian-edition titles; manual entry is the fallback.
- Users accept approximate (not precise) location sharing.
- Free-tier or low-cost cloud services are sufficient up to the first 10k users.

## 16. Constraints

- **Team:** small team (solo to 3 engineers), so modular monolith and managed services.
- **Budget:** low infrastructure budget; prefer managed, pay-as-you-go services.
- **Stack:** React + TypeScript + Tailwind; FastAPI (Python); PostgreSQL; Redis; SQLAlchemy; Cloudinary; Docker; AWS.
- **Legal:** DPDP Act 2023, IT Rules for intermediaries (grievance officer, takedown timelines).
- **Platform:** web first; mobile app deferred.
- **Trust:** no payments handling in v1 (avoids payment-regulation scope).

## 17. Product Roadmap

| Phase | Timeline | Theme | Key deliverables | Exit criteria |
| --- | --- | --- | --- | --- |
| **0. Foundations** | Weeks 1–3 | Platform setup | Repo, CI/CD, Docker, IaC, schema, auth, RBAC, logging, config | Deployed skeleton on staging |
| **1. Core Loop (MVP)** | Weeks 4–10 | Lend and borrow | Listings, images, search, exchange state machine, notifications, reviews, trust v1, admin | Closed beta ready |
| **2. Beta** | Weeks 11–14 | Prove liquidity | Chat polish, wishlist, reminders, moderation, load tests, one-city launch | 500 exchanges, return rate ≥ 85% |
| **3. Community** | Months 4–6 | Retention | Reading clubs, Book Journey, dashboard, push, real-time chat, Hindi | M3 retention ≥ 30% |
| **4. Scale** | Months 7–9 | Growth and quality | Search service with ranking, caching tuning, spam ML, dispute tooling, NGO drives | 100k MAU, p95 \< 300 ms |
| **5. Intelligence** | Months 10–12 | Differentiation | Semantic search, recommendations, barcode/OCR, QR pickup | Recommendation CTR uplift ≥ 15% |
| **6. Network effects** | Year 2 | Moat | Chain exchange matching, library integration, mobile app, service extraction | Multi-city, multi-institution |

---

## Open Questions

1. Should low-trust new users be allowed to borrow high-value books (security deposit alternative)?
2. How do we verify institutional accounts (NGO, library)?
3. What is the acceptable overdue policy before escalating to a dispute?
4. Do we show book "list price" for money-saved calculations, and from which source?

## Appendix: Suggested Next Documents

High-level design (bounded contexts, event flows, outbox), database schema and ER diagram, OpenAPI contract, exchange state-machine spec, trust-score algorithm spec, and threat model.