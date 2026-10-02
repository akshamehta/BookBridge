# BookBridge: REST API Specification (v1)

**Base URL:** `https://api.bookbridge.in/v1` · **Format:** JSON (`application/json`), UTF-8 · **Spec:** published as OpenAPI 3.1 at `/v1/openapi.json`.

---

## 1. Global Conventions (apply to every endpoint)

| Topic | Rule |
| --- | --- |
| **Resources** | Plural nouns, lowercase, kebab-case (`/pickup-proposals`). IDs are UUIDv7 strings. Nesting max 2 levels |
| **Methods** | `GET` safe/idempotent · `POST` create or non-CRUD action · `PUT` full replace/idempotent set · `PATCH` partial update (JSON Merge Patch) · `DELETE` remove |
| **State transitions** | Modelled as `POST /resource/{id}/<verb>` (e.g. `/accept`). Each has its own authorisation, validation and event, and generic PATCH of `state` is intentionally not allowed |
| **Auth header** | `Authorization: Bearer <access_jwt>` (15 min). Refresh token travels only in an `HttpOnly; Secure; SameSite=Strict` cookie |
| **Idempotency** | `Idempotency-Key: <uuid>` header on all `POST` mutations marked ⚑. Same key + same body replays the stored response for 24 h; same key + different body → `409 IDEMPOTENCY_KEY_REUSED` |
| **Concurrency** | Resources with `version` return `ETag`. `PATCH`/`DELETE` on them require `If-Match`. Mismatch → `412 PRECONDITION_FAILED`; missing → `428 PRECONDITION_REQUIRED` |
| **Timestamps/units** | ISO-8601 UTC; distances in km; money in paise (integer) |
| **Unknown fields** | Rejected (`extra=forbid`) → 422. Client can never set `id`, `owner_id`, `status`-like server fields |
| **Rate limit headers** | `X-RateLimit-Limit/Remaining/Reset`; 429 adds `Retry-After` |
| **Tracing** | Every response has `X-Request-ID` (also in error body) |
| **Versioning** | URL major version; additive changes only inside v1; `Deprecation`/`Sunset` headers when retiring |

### 1.1 Auth Legend

**Public** no token · **User** valid token, status `active` · **Verified** User with verified email · **Owner/Borrower/Participant** resource-level relationship checked by policy · **ClubRole(x)** member role in that club · **Moderator** · **Admin**.

### 1.2 Pagination (all list endpoints)

**Cursor-based (keyset)**, never offset. Query: `limit` (1–100, default 20), `cursor` (opaque, from `next_cursor`).

```
{ "data": [ ... ], "page": { "next_cursor": "eyJ…" | null, "limit": 20, "has_more": true } }
```

Invalid/expired cursor → `400 INVALID_CURSOR`. Sorting is stable with a tiebreaker on `id`. Cursor encodes the sort key, so changing `sort` invalidates it. *Why cursor:* constant-time at depth, no skipped/duplicated rows under concurrent writes. Totals are not returned by default (expensive); `include_total=true` available on admin lists only.

### 1.3 Filtering and Sorting

Filters are flat query parameters (`state=borrowed`, `min_condition=good`). Multi-value: comma-separated (`genre=fiction,history`). Range: `_from`/`_to` suffix. Sorting: `sort=<field>` ascending, `sort=-<field>` descending; only whitelisted fields (others → `422 INVALID_SORT_FIELD`). Sparse fields: `fields=` not supported in v1 (keeps caching simple).

### 1.4 Error Format (RFC 7807 `application/problem+json`)

```
{ "type": "https://api.bookbridge.in/errors/VALIDATION_FAILED", "title": "...", "status": 422,
  "code": "VALIDATION_FAILED", "detail": "...", "request_id": "...",
  "errors": [ { "field": "isbn", "code": "INVALID_ISBN13", "message": "..." } ] }
```

### 1.5 Shared Error Codes (any endpoint may return)

| Status | Code | When |
| --- | --- | --- |
| 400 | `MALFORMED_REQUEST` / `INVALID_CURSOR` | Bad JSON, bad cursor |
| 401 | `UNAUTHENTICATED` / `TOKEN_EXPIRED` / `TOKEN_REVOKED` | Missing, expired or revoked token |
| 403 | `FORBIDDEN` / `ACCOUNT_SUSPENDED` / `EMAIL_NOT_VERIFIED` | Policy or account state denies |
| 404 | `NOT_FOUND` | Missing **or** not visible to caller (avoids existence leaks) |
| 405/406/415 | `METHOD_NOT_ALLOWED` / `NOT_ACCEPTABLE` / `UNSUPPORTED_MEDIA_TYPE` | Protocol errors |
| 409 | `CONFLICT` (specific codes below) | State conflict |
| 412/428 | `PRECONDITION_FAILED` / `PRECONDITION_REQUIRED` | ETag handling |
| 413 | `PAYLOAD_TOO_LARGE` | Body > 1 MB |
| 422 | `VALIDATION_FAILED` / `INVALID_SORT_FIELD` / `INVALID_FILTER` | Semantic validation |
| 429 | `RATE_LIMITED` | Limit exceeded |
| 500/503 | `INTERNAL_ERROR` / `DEPENDENCY_UNAVAILABLE` | Server/dependency failure |

In the tables below, **Errors** lists only *endpoint-specific* codes, in addition to the shared ones. Success statuses are in the **Response** column.

### 1.6 Shared Schemas

- **UserSummary** `{id, display_name, avatar_url, city, college, trust_score, trust_label}`
- **ListingCard** `{id, copy_id, book:{id,title,authors[],cover_url,language,isbn13}, exchange_type, condition, status, distance_km?, owner:UserSummary, primary_image_url, created_at}`
- **ListingDetail** = ListingCard + `{edition, publisher, genres[], description, owner_notes, images[], max_loan_days, approx_location:{lat,lng}, version}`
- **Exchange** `{id, state, exchange_type, listing:ListingCard, borrower:UserSummary, owner:UserSummary, requested_days, due_on, pickup?, conversation_id?, allowed_actions[], expires_at, created_at, version}` (`allowed_actions` tells the UI which transitions are legal for the caller)

---

## 2. Authentication and Profile APIs

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /auth/register` ⚑ | Public | `{email, password, display_name, city_id?, college_id?, accept_terms}` | **201** `{user:{id,email,status:"pending_verification"}}` + verification email | Email RFC-valid, ≤254, normalised lowercase; password 10–128 chars, not in breached list, not equal to email; display_name 2–60; `accept_terms` must be true; age consent | 409 `EMAIL_ALREADY_REGISTERED` (response deliberately generic with 202 in strict mode to prevent enumeration) |
| 2 | `POST /auth/verify-email` | Public | `{token}` | **204** | Token 43-char url-safe | 400 `TOKEN_INVALID`, 410 `TOKEN_EXPIRED` |
| 3 | `POST /auth/resend-verification` | Public | `{email}` | **202** (always, no enumeration) | Email format | 429 `RATE_LIMITED` (3/h) |
| 4 | `POST /auth/login` | Public | `{email, password}` | **200** `{access_token, token_type:"Bearer", expires_in:900, user:{id,roles[],display_name}}` + `Set-Cookie` refresh | Both required | 401 `INVALID_CREDENTIALS` (generic), 423 `ACCOUNT_LOCKED` (after 5 failures, 15 min), 403 `EMAIL_NOT_VERIFIED`, 403 `ACCOUNT_SUSPENDED` |
| 5 | `POST /auth/google` | Public | `{id_token}` | **200** (same as login), **201** if new account | Token verified against Google JWKS; `aud`, `exp`, `email_verified=true` | 401 `GOOGLE_TOKEN_INVALID`, 409 `ACCOUNT_LINK_REQUIRED` (email exists with password) |
| 6 | `POST /auth/refresh` | Refresh cookie | none (cookie) | **200** `{access_token, expires_in}` + rotated cookie | Cookie present, hash matches active token | 401 `REFRESH_INVALID`; `REFRESH_REUSED` (revokes family, forces re-login) |
| 7 | `POST /auth/logout` | User | none | **204**, cookie cleared, refresh revoked, access `jti` denylisted | — | — |
| 8 | `POST /auth/logout-all` | User | none | **204** | — | — |
| 9 | `POST /auth/password/forgot` | Public | `{email}` | **202** always | Email format | 429 (3/h per email+IP) |
| 10 | `POST /auth/password/reset` | Public | `{token, new_password}` | **204**, all sessions revoked | Password policy as #1; token single-use | 400 `TOKEN_INVALID`, 410 `TOKEN_EXPIRED` |
| 11 | `POST /auth/password/change` | User | `{current_password, new_password}` | **204** | Different from current; policy | 401 `INVALID_CREDENTIALS` |
| 12 | `GET /users/me` | User | — | **200** full profile `{id,email,display_name,bio,avatar_url,city,college,interests[],favorite_genres[],trust:{score,breakdown},roles[],created_at,version}` + `ETag` | — | — |
| 13 | `PATCH /users/me` | User | any of `{display_name, bio, city_id, college_id, interests[], favorite_genre_ids[], search_radius_km, locale}` + `If-Match` | **200** profile | display_name 2–60; bio ≤500, sanitised; ids exist; interests ≤15; genres ≤10; radius 1–100; `college.city = city` | 412 `PRECONDITION_FAILED` |
| 14 | `PUT /users/me/avatar` | User | `{asset_id}` | **200** `{avatar_url}` | Asset owned by caller, `ready`, image/jpeg\|png\|webp ≤5 MB | 404 `ASSET_NOT_FOUND`, 422 `ASSET_NOT_IMAGE` |
| 15 | `GET /users/{id}` | User | — | **200** public profile (no email, fuzzy location, trust summary, counts) | UUID | 404 (also if blocked/banned) |
| 16 | `GET /users/me/dashboard` | User | — | **200** `{books_read,books_borrowed,books_lent,books_donated,reading_streak,money_saved_paise,co2_saved_grams,favorite_genres[]}` | — | — |
| 17 | `GET /users/me/reading-history` | User | — | **200** Page of `{id,book,status,started_on,finished_on,rating}` | — | — |
| 18 | `POST /users/me/reading-history` | User | `{book_id, status, started_on?, finished_on?, rating?}` | **201** | `finished_on ≥ started_on`; rating 1–5; unique (user, book, started_on) | 409 `ALREADY_LOGGED` |
| 19 | `POST /users/{id}/block` / `DELETE /users/{id}/block` | User | none | **204** | Cannot block self | 422 `CANNOT_BLOCK_SELF` |
| 20 | `POST /users/me/data-export` | User | none | **202** `{job_id}` (emailed link) | — | 429 (1/day) |
| 21 | `DELETE /users/me` | User | `{password}` (or Google reauth) | **202** (soft-delete now, anonymise after 30 days) | Password re-check; no open exchanges | 409 `OPEN_EXCHANGES_EXIST` |
| 22 | `GET /genres`, `GET /cities`, `GET /colleges` | Public | — | **200** Page of reference rows; cacheable (`Cache-Control: public, max-age=3600`, ETag) | — | — |

**List params:** #17 `status`, `sort=-finished_on`; #22 `q` (prefix match), `city_id` (colleges), `sort=name`.

---

## 3. Book (Listing) APIs

*A "listing" request creates the book (if new), the physical copy and its offer atomically.*

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /uploads/signatures` | Verified | `{purpose: "listing_image"\|"avatar"\|"chat", mime_type, bytes}` | **201** `{asset_id, upload_url, fields, expires_in:300}` | MIME allow-list (jpeg/png/webp); bytes ≤5 MB; ≤30 per hour | 429 |
| 2 | `GET /isbn/{isbn}` | User | — | **200** `{isbn13, title, authors[], publisher, language, edition, cover_url, source}` | ISBN-10/13 with checksum; normalised to 13 | 404 `ISBN_NOT_FOUND` (client falls back to manual entry), 422 `INVALID_ISBN` |
| 3 | `POST /listings` ⚑ | Verified | `{book:{book_id? \| isbn13?, title, authors[], publisher?, language, edition?, genre_ids[], description?}, condition, condition_notes?, exchange_type, max_loan_days?, owner_notes?, image_asset_ids[1..6], pickup_area?}` | **201** ListingDetail + `Location` header | Exactly one of `book_id` or manual `book` fields; title ≤200; ≥1 author; language ISO-639-1; genres ≤5; `exchange_type` ∈ lend/exchange/donate; `max_loan_days` 1–90 and only for `lend`; condition enum; images owned, ready, ≤6; user listing cap (e.g. 500) | 404 `BOOK_NOT_FOUND`, 409 `DUPLICATE_LISTING` (same user + same ISBN within 24 h), 422 `ASSET_NOT_READY`, 403 `LISTING_LIMIT_REACHED` |
| 4 | `GET /listings/{id}` | Public (limited) / User | — | **200** ListingDetail + `ETag`. Public view hides owner contact and shows approx. location | UUID | 404 (deleted, taken down or hidden) |
| 5 | `PATCH /listings/{id}` | Owner | any of `{condition, condition_notes, exchange_type, max_loan_days, owner_notes, description, genre_ids}` + `If-Match` | **200** ListingDetail | Same field rules as #3; **title/author/ISBN immutable** after creation (create a new listing instead); `exchange_type` locked while an exchange is live | 409 `LISTING_LOCKED` (live exchange), 412 |
| 6 | `PATCH /listings/{id}/availability` | Owner | `{is_active: bool}` | **200** `{is_active, status}` | Cannot activate if copy is `borrowed`/`reserved`/`donated` | 409 `COPY_NOT_AVAILABLE` |
| 7 | `DELETE /listings/{id}` | Owner | + `If-Match` | **204** (soft delete) | — | 409 `OPEN_EXCHANGE_EXISTS` |
| 8 | `POST /listings/{id}/images` | Owner | `{asset_id, position?}` | **201** `{image:{id,url,position}}` | Max 6 images; asset ready and owned | 409 `IMAGE_LIMIT_REACHED` |
| 9 | `PUT /listings/{id}/images/order` | Owner | `{image_ids:[...]}` | **200** images in new order | Must be a permutation of current images | 422 `INVALID_ORDER` |
| 10 | `DELETE /listings/{id}/images/{image_id}` | Owner | none | **204** | Cannot remove last image | 409 `LAST_IMAGE` |
| 11 | `GET /me/listings` | User | — | **200** Page of ListingCard + `open_requests_count` | — | — |
| 12 | `GET /books/{id}` | Public | — | **200** `{id,title,authors[],publisher,language,edition,genres[],description,cover_url,rating:{avg,count},available_copies_count}` | — | 404 |
| 13 | `GET /books/{id}/listings` | User | — | **200** Page of ListingCard (available copies nearby) | — | 404 |
| 14 | `GET /copies/{id}/journey` | Public | — | **200** `{copy:{id,book,current_owner?}, entries:[{id,reader:UserSummary,borrowed_on,returned_on,review_excerpt?,favorite_quote?,lessons_learned?}]}`. Only `is_public` entries; reader identity shown per their privacy setting | — | 404 |
| 15 | `PATCH /journey-entries/{id}` | Entry's reader | `{favorite_quote?, lessons_learned?, is_public?}` | **200** | Quote ≤500; lessons ≤1000; sanitised; allowed only after the exchange is `completed` | 409 `EXCHANGE_NOT_COMPLETED` |

**List params**

- #11: filter `status` (available|reserved|borrowed|exchanged|donated), `exchange_type`, `is_active`; sort `-created_at` (default), `title`.
- #13: filter `exchange_type`, `min_condition`, `max_distance_km` (needs caller location); sort `distance` (default), `-trust`, `-created_at`.
- #14: sort `-borrowed_on` (default), cursor-paginated.

---

## 4. Search APIs

| # | Endpoint | Auth | Request (query params) | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `GET /search/listings` | Public (rate-limited) / User (personalised ranking, distance) | **Text:** `q` (title, author, ISBN or free text). **Filters:** `isbn`, `author`, `genre` (csv slugs), `language` (csv), `city_id`, `college_id`, `exchange_type` (csv: lend,exchange,donate), `min_condition`, `availability` (`available` default \| `all`), `lat`,`lng`,`radius_km`, `exchange_only`, `donation_only`, `borrow_only`. **Sort:** `relevance` (default), `distance`, `-created_at`, `-trust`. **Page:** `limit`, `cursor` | **200** `{data:[ListingCard + highlight], page, facets:{genre:[{key,count}],language:[…],condition:[…],exchange_type:[…]}, took_ms}` + `Cache-Control: private, max-age=30` | `q` 1–100 chars, sanitised; `lat` −90..90, `lng` −180..180, both or neither; `radius_km` 1–100 (default 10); `sort=distance` requires lat/lng or a logged-in user with home location; `isbn` checksum; csv lists ≤10 items; `exchange_only`/`donation_only`/`borrow_only` are shortcuts, mutually exclusive | 422 `GEO_PARAMS_INCOMPLETE`, `INVALID_SORT_FIELD`, `FILTER_CONFLICT`; 503 `SEARCH_DEGRADED` (**falls back to basic DB search, flagged by `X-Search-Mode: fallback`**) |
| 2 | `GET /search/suggest` | Public | `q` (2–50 chars), `type` (`title`\|`author`\|`isbn`, default all), `limit` ≤10 | **200** `{suggestions:[{text,type,book_id?}]}` | q min length 2 | 429 (strict limit) |
| 3 | `GET /search/books` | Public | Same text filters as #1 (no distance); sort `relevance`, `-rating`, `-available_copies` | **200** Page of book summaries with `available_copies_count` | as #1 | as #1 |
| 4 | `GET /search/clubs` | User | `q`, `city_id`, `college_id`, `is_private=false`, sort `relevance`, `-member_count` | **200** Page of club cards | as #1 | — |

*Notes:* Search is a **GET with query parameters** (cacheable, linkable). Results are an eventually consistent read model; availability is re-verified on `POST /exchanges`. Deep pagination beyond \~1,000 hits is capped (`400 SEARCH_WINDOW_EXCEEDED`) because ranking stability degrades.

---

## 5. Exchange APIs

*State machine:* `requested → accepted → pickup_scheduled → borrowed → return_pending → returned → completed`; branches `rejected`, `cancelled`, `expired`, `disputed`. Every action returns the updated **Exchange** (with new `ETag` and `allowed_actions`).

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /exchanges` ⚑ | Verified (borrower) | `{listing_id, requested_days?, message?}` | **201** Exchange (`requested`) | Listing active and copy `available`; caller ≠ owner; not blocked either way; `requested_days` ≤ listing `max_loan_days` (lend only); message ≤500; caller trust ≥ listing minimum; ≤5 open requests per borrower, ≤20 per day | 404 `LISTING_NOT_FOUND`, 409 `COPY_NOT_AVAILABLE`, 409 `DUPLICATE_REQUEST`, 403 `TRUST_TOO_LOW`, 403 `SELF_REQUEST_NOT_ALLOWED`, 429 `REQUEST_QUOTA_EXCEEDED` |
| 2 | `GET /exchanges` | User | — | **200** Page of Exchange | — | — |
| 3 | `GET /exchanges/{id}` | Participant | — | **200** Exchange + `ETag` | — | 404 |
| 4 | `POST /exchanges/{id}/accept` ⚑ | Owner | `{note?}` | **200** (`accepted`; copy → `reserved`; conversation opened; competing requests auto-declined) | State = `requested`; not expired | 409 `INVALID_STATE_TRANSITION`, 409 `COPY_NOT_AVAILABLE`, 410 `REQUEST_EXPIRED` |
| 5 | `POST /exchanges/{id}/reject` ⚑ | Owner | `{reason_code, note?}` | **200** (`rejected`) | State = `requested`; reason ∈ enum | 409 `INVALID_STATE_TRANSITION` |
| 6 | `POST /exchanges/{id}/cancel` ⚑ | Participant | `{reason_code, note?}` | **200** (`cancelled`; copy → `available` if reserved) | State ∈ requested, accepted, pickup_scheduled (not after handover) | 409 `INVALID_STATE_TRANSITION`. *Counts toward cancellation rate* |
| 7 | `POST /exchanges/{id}/pickup-proposals` | Participant | `{place_text, place_lat?, place_lng?, proposed_time}` | **201** `{id,status:"proposed",…}` | State ∈ accepted/pickup_scheduled; time in future and ≤14 days; place_text 3–200 | 409 `INVALID_STATE_TRANSITION`, 422 `TIME_IN_PAST` |
| 8 | `POST /exchanges/{id}/pickup-proposals/{pid}/accept` | The *other* participant | none | **200** (`pickup_scheduled`) | Proposal `proposed`; cannot accept own | 403 `CANNOT_ACCEPT_OWN_PROPOSAL`, 409 `PROPOSAL_NOT_OPEN` |
| 9 | `POST /exchanges/{id}/pickup-proposals/{pid}/reject` | The *other* participant | `{note?}` | **200** | as #8 | as #8 |
| 10 | `POST /exchanges/{id}/confirm-handover` ⚑ | Participant | `{}` | **200**. Moves to `borrowed` (lend, `due_on` set) or `completed` (exchange/donate, ownership transferred) **when both parties have confirmed** | State = `pickup_scheduled`; each party confirms once (idempotent) | 409 `INVALID_STATE_TRANSITION` |
| 11 | `POST /exchanges/{id}/confirm-return` ⚑ | Participant | `{condition_on_return?}` | **200**. After both confirm → `returned` → `completed`; copy → `available` | State ∈ borrowed/return_pending; condition enum | 409 `INVALID_STATE_TRANSITION` |
| 12 | `POST /exchanges/{id}/extensions` | Borrower | `{new_due_on, reason?}` | **201** `{id,status:"pending"}` | State = `borrowed`; new date > current due and ≤ 30 days later; one pending at a time | 409 `EXTENSION_PENDING`, 422 `INVALID_DUE_DATE` |
| 13 | `POST /exchanges/{id}/extensions/{eid}/decision` | Owner | `{decision: "approve"\|"reject"}` | **200** | Extension `pending` | 409 `EXTENSION_NOT_PENDING` |
| 14 | `POST /exchanges/{id}/disputes` ⚑ | Participant | `{reason:"not_returned"\|"damaged"\|"other", description, evidence_asset_ids[0..5]}` | **201** `{id,status:"open"}`; exchange → `disputed` | State ∈ borrowed/return_pending/returned; description 20–2000; one open dispute per exchange; not-returned only after `due_on` | 409 `DISPUTE_EXISTS`, 422 `NOT_YET_OVERDUE` |
| 15 | `GET /exchanges/{id}/history` | Participant | — | **200** Page of `{from_state,to_state,actor,reason,created_at}` | — | — |

**#2 list params:** filters `role` (`borrower`|`owner`|`any`, default any), `state` (csv), `exchange_type`, `listing_id`, `created_from`/`created_to`, `overdue=true`; sort `-created_at` (default), `due_on`, `-updated_at`; cursor pagination.

---

## 6. Review and Trust APIs

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /exchanges/{id}/reviews` ⚑ | Participant | `{subject_type:"book"\|"exchange"\|"user", rating (1–5), title?, body?}` (book: implicit from the exchange's book; user: the counterpart) | **201** Review | Exchange `completed`; one review per (exchange, reviewer, subject_type); within 30 days of completion; rating integer 1–5; body ≤2000, sanitised; title ≤100 | 409 `ALREADY_REVIEWED`, 409 `EXCHANGE_NOT_COMPLETED`, 410 `REVIEW_WINDOW_CLOSED` |
| 2 | `GET /books/{id}/reviews` | Public | — | **200** Page + `summary:{avg,count,distribution{1..5}}` | — | 404 |
| 3 | `GET /users/{id}/reviews` | User | — | **200** Page of reviews received (reviewer shown) + summary | — | 404 |
| 4 | `GET /users/{id}/trust` | User | — | **200** `{score, label, breakdown:{successful_exchanges, on_time_return_rate, avg_rating, cancellation_rate, median_response_minutes}, computed_at}` (own profile adds improvement tips) | — | 404 |
| 5 | `PATCH /reviews/{id}` | Author | `{rating?, title?, body?}` + `If-Match` | **200** | Within 7 days of posting; same rules as #1 | 403 `EDIT_WINDOW_CLOSED`, 412 |
| 6 | `DELETE /reviews/{id}` | Author | none | **204** (soft; trust recomputed) | — | — |
| 7 | `POST /reviews/{id}/reply` | Reviewed user | `{body}` | **201** | One reply; ≤1000 chars | 409 `ALREADY_REPLIED` |

**List params (#2, #3):** filters `min_rating`, `max_rating`, `with_text=true`; sort `-created_at` (default), `-rating`, `rating`. Reporting a review uses `POST /reports` (§10).

---

## 7. Wishlist APIs

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `GET /wishlist` | User | — | **200** Page of `{id,book,radius_km,notify,fulfilled_at,available_now_count,created_at}` | — | — |
| 2 | `POST /wishlist` ⚑ | User | `{book_id \| isbn13 \| {title,author}, radius_km?, notify?}` | **201** item (non-catalogued title creates a pending book stub) | One identifier form only; radius 1–100 (default profile radius); cap 200 items | 409 `ALREADY_IN_WISHLIST`, 403 `WISHLIST_LIMIT_REACHED` |
| 3 | `PATCH /wishlist/{id}` | Owner | `{radius_km?, notify?}` | **200** | as #2 | 404 |
| 4 | `DELETE /wishlist/{id}` | Owner | none | **204** | — | 404 |

**#1 list params:** filters `fulfilled` (bool), `available_now` (bool); sort `-created_at` (default), `title`. Fulfilment is *event-driven*, not an API: a new matching listing triggers a `wishlist_fulfilled` notification.

---

## 8. Reading Club APIs

*Club roles:* `owner` > `moderator` > `member`. Private clubs are visible only to members (and invite holders).

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /clubs` ⚑ | Verified | `{name, description?, is_private, city_id?, college_id?, cover_asset_id?}` | **201** Club | name 3–60, unique slug; description ≤1000; ≤5 owned clubs | 409 `CLUB_NAME_TAKEN`, 403 `CLUB_LIMIT_REACHED` |
| 2 | `GET /clubs` | User | — | **200** Page of club cards (`member_count`, `my_role?`) | — | — |
| 3 | `GET /clubs/{id}` | User (public) / Member (private) | — | **200** Club + `my_membership` | — | 404 |
| 4 | `PATCH /clubs/{id}` | ClubRole(owner) | any of name, description, is_private, cover_asset_id + `If-Match` | **200** | as #1 | 412 |
| 5 | `DELETE /clubs/{id}` | ClubRole(owner) | none | **204** (soft) | — | — |
| 6 | `POST /clubs/{id}/members` | User | `{invite_code?, message?}` | **201** `{status:"active"\|"pending"}` (public = active, private = pending approval) | Not already a member; invite code valid if private | 409 `ALREADY_MEMBER`, 403 `BANNED_FROM_CLUB` |
| 7 | `GET /clubs/{id}/members` | Member | — | **200** Page of `{user:UserSummary, role, status, joined_at}` | — | 403 |
| 8 | `PATCH /clubs/{id}/members/{user_id}` | ClubRole(owner/moderator) | `{role?, status?: "active"\|"removed"}` | **200** | Only owner assigns moderator; cannot demote owner | 403 `INSUFFICIENT_CLUB_ROLE` |
| 9 | `DELETE /clubs/{id}/members/me` | Member | none | **204** | Owner must transfer ownership first | 409 `OWNER_CANNOT_LEAVE` |
| 10 | `DELETE /clubs/{id}/members/{user_id}` | ClubRole(moderator+) | none | **204** | Cannot remove owner | 403 |
| 11 | `GET/POST /clubs/{id}/schedule` | Member / ClubRole(moderator+) | POST `{book_id, starts_on, ends_on, target_notes?}` | **200** list / **201** item | `ends_on ≥ starts_on`; no overlapping items | 409 `SCHEDULE_OVERLAP` |
| 12 | `PATCH`/`DELETE /clubs/{id}/schedule/{sid}` | ClubRole(moderator+) | partial fields | **200** / **204** | as #11 | 404 |
| 13 | `GET/POST /clubs/{id}/threads` | Member | POST `{title, body}` | **200** Page / **201** thread | title 3–120; body ≤5000 sanitised | 429 |
| 14 | `GET /clubs/{id}/threads/{tid}/posts` | Member | — | **200** Page of posts | — | 404 |
| 15 | `POST /clubs/{id}/threads/{tid}/posts` | Member | `{body, parent_post_id?}` | **201** | body ≤3000; parent in same thread, max depth 1; thread not locked | 409 `THREAD_LOCKED` |
| 16 | `PATCH /clubs/{id}/threads/{tid}` | ClubRole(moderator+) | `{is_pinned?, is_locked?}` | **200** | — | 403 |
| 17 | `DELETE /clubs/{id}/posts/{post_id}` | Author or ClubRole(moderator+) | none | **204** | — | 403 |
| 18 | `POST /clubs/{id}/polls` | ClubRole(moderator+) | `{question, options[2..10], closes_at, multi_select}` | **201** | question ≤200; options unique, ≤100 chars; `closes_at` future, ≤30 days | 422 |
| 19 | `GET /clubs/{id}/polls` | Member | — | **200** Page with results (shown after voting or close) | — | — |
| 20 | `PUT /clubs/{id}/polls/{pid}/vote` | Member | `{option_ids[]}` | **200** updated tallies (idempotent replace of own vote) | Poll open; 1 option unless `multi_select`; options belong to poll | 409 `POLL_CLOSED`, 422 `TOO_MANY_OPTIONS` |
| 21 | `GET/POST /clubs/{id}/events` | Member / ClubRole(moderator+) | POST `{title, description?, starts_at, ends_at, location_text, lat?, lng?, capacity?}` | **200** Page / **201** | `ends_at > starts_at`; starts in future; capacity 2–1000 | 422 |
| 22 | `PATCH`/`DELETE /clubs/{id}/events/{eid}` | ClubRole(moderator+) | partial | **200** / **204** (attendees notified) | as #21 | — |
| 23 | `PUT /clubs/{id}/events/{eid}/rsvp` | Member | `{status:"going"\|"maybe"\|"no"}` | **200** `{status, going_count}` | Event not past; capacity respected | 409 `EVENT_FULL` |

**List params:** #2 filters `q`, `city_id`, `college_id`, `is_private`, `joined=true`; sort `-member_count`, `-created_at`, `name`. #7 filter `role`, `status`; sort `joined_at`. #13 sort `-last_activity` (default), `-created_at`; filter `pinned`. #14 sort `created_at` (asc, default). #19 filter `open=true`. #21 filters `from`, `to`, `upcoming=true`; sort `starts_at`.

---

## 9. Chat APIs

*Gating rule:* a conversation exists **only** for an `accepted+` exchange; there is no endpoint to create one directly. It closes N days after completion (read-only).

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `GET /conversations` | User | — | **200** Page of `{id, exchange_id, counterpart:UserSummary, book_title, last_message, unread_count, status, last_message_at}` | — | — |
| 2 | `GET /conversations/{id}` | Participant | — | **200** conversation + exchange summary | — | 404 |
| 3 | `GET /conversations/{id}/messages` | Participant | — | **200** Page of `{id, sender_id, kind, body, attachments[], created_at, read_by_counterpart}` | — | 404 |
| 4 | `POST /conversations/{id}/messages` ⚑ | Participant | `{client_msg_id (uuid), kind:"text"\|"image", body?, attachment_asset_ids[0..3]}` | **201** message (idempotent on `client_msg_id`) | Conversation `open`; text 1–2000 chars, sanitised; image kind requires ≥1 ready image asset; neither party blocked; rate limit 30/min | 409 `CONVERSATION_CLOSED`, 403 `BLOCKED`, 422 `EMPTY_MESSAGE`, 429 |
| 5 | `POST /conversations/{id}/read` | Participant | `{last_read_message_id}` | **204** (updates read cursor, broadcasts receipt) | ID belongs to conversation and is ≥ current cursor | 422 `INVALID_MESSAGE_ID` |
| 6 | `DELETE /conversations/{id}/messages/{mid}` | Sender | none | **204** (soft delete, shown as "message removed") | Within 15 min of sending | 403 `DELETE_WINDOW_CLOSED` |
| 7 | `PATCH /conversations/{id}` | Participant | `{muted: bool}` | **200** | — | — |
| 8 | `GET /realtime` (WebSocket upgrade) | User (`?ticket=` short-lived, from `POST /realtime/tickets`) | Frames: `message.send`, `typing`, `read`, `ping` | Server events: `message.new`, `message.read`, `typing`, `notification.new`, `exchange.updated` | Ticket single-use, 30 s; frame size ≤16 KB | 401 on invalid ticket; close codes 4401/4403/4429 |
| 9 | `POST /realtime/tickets` | User | none | **201** `{ticket, expires_in:30}` | — | — |

**List params:** #1 filters `unread=true`, `status`; sort `-last_message_at` (default). #3 sort by `id` only: `before=<message_id>` (older, default) or `after=<message_id>` (newer, for catch-up after reconnect); `limit` ≤100. REST remains the source of truth; the WebSocket is a delivery optimisation, so clients must work with REST polling alone.

---

## 10. Notification APIs

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `GET /notifications` | User | — | **200** Page of `{id, type, title, body, entity:{type,id}, read_at, created_at}` | — | — |
| 2 | `GET /notifications/unread-count` | User | — | **200** `{count}` (cached, ≤1 s stale) | — | — |
| 3 | `POST /notifications/read` | User | `{ids?:[…≤100], all?:true}` | **204** | Exactly one of `ids`/`all` | 422 `AMBIGUOUS_SELECTION` |
| 4 | `PATCH /notifications/{id}` | User | `{read: bool}` | **200** | — | 404 |
| 5 | `DELETE /notifications/{id}` | User | none | **204** | — | — |
| 6 | `GET /notifications/preferences` | User | — | **200** matrix `[{type, channels:{in_app,email,push}, }]` + `quiet_hours{start,end,tz}` | — | — |
| 7 | `PUT /notifications/preferences` | User | full matrix + quiet hours | **200** | Types and channels in enum; mandatory types (security, exchange status) cannot disable `in_app`; `start≠end`; valid tz | 422 `MANDATORY_NOTIFICATION` |
| 8 | `POST /notifications/devices` | User | `{platform:"ios"\|"android"\|"web", token}` | **201** | Token ≤4096, unique upsert | — |
| 9 | `DELETE /notifications/devices/{id}` | User | none | **204** | — | — |

**#1 list params:** filters `unread=true`, `type` (csv: exchange_accepted, exchange_rejected, wishlist_fulfilled, return_reminder, chat_message, club_update), `created_from`; sort `-created_at` (default). Notifications are created by the system only; there is no client `POST` to create one.

---

## 11. Report and Admin APIs

### 11.1 User-facing reporting

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `POST /reports` ⚑ | Verified | `{target_type: "user"\|"listing"\|"message"\|"review"\|"club"\|"post", target_id, reason: "spam"\|"abuse"\|"fake"\|"unsafe"\|"other", details?}` | **201** `{id, status:"open"}` | Target exists and is visible to reporter; details ≤1000; cannot report self | 409 `ALREADY_REPORTED` (same target, 24 h), 429 (20/day) |

### 11.2 Admin (prefix `/admin`; all require Moderator unless noted; every mutation writes `audit_logs`)

| # | Endpoint | Auth | Request | Response | Validation | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `GET /admin/users` | Moderator | — | **200** Page of admin user view (email, status, trust, reports count, last_login) | — | — |
| 2 | `GET /admin/users/{id}` | Moderator | — | **200** full record + moderation history + recent exchanges | — | 404 |
| 3 | `POST /admin/users/{id}/suspend` ⚑ | Moderator | `{reason, duration_days (1–365), notify:bool}` | **200** `{status:"suspended", until}`; sessions revoked | Reason 10–500; cannot act on equal/higher role | 403 `CANNOT_MODERATE_PEER`, 409 `ALREADY_SUSPENDED` |
| 4 | `POST /admin/users/{id}/ban` ⚑ | Admin | `{reason}` | **200** `{status:"banned"}`; listings hidden, open exchanges cancelled | Reason required | 403, 409 |
| 5 | `POST /admin/users/{id}/restore` ⚑ | Admin | `{reason}` | **200** | Must be suspended/banned | 409 `NOT_RESTRICTED` |
| 6 | `PUT /admin/users/{id}/roles` | Admin | `{roles: [...]}` | **200** | Roles in enum; cannot remove last admin; cannot self-demote | 409 `LAST_ADMIN` |
| 7 | `GET /admin/listings` | Moderator | — | **200** Page incl. hidden/taken-down | — | — |
| 8 | `POST /admin/listings/{id}/takedown` ⚑ | Moderator | `{reason_code, note?}` | **200**; owner notified; live exchanges cancelled | State not already taken down | 409 `ALREADY_TAKEN_DOWN` |
| 9 | `POST /admin/listings/{id}/restore` | Moderator | `{note?}` | **200** | Currently taken down | 409 |
| 10 | `GET /admin/reports` | Moderator | — | **200** Page with SLA clock (`age_hours`, `sla_breached`) | — | — |
| 11 | `GET /admin/reports/{id}` | Moderator | — | **200** report + target snapshot + related reports/history | — | 404 |
| 12 | `PATCH /admin/reports/{id}` | Moderator | `{assigned_to?, status?: "in_review"}` | **200** | Assignee is a moderator | 409 `ALREADY_ASSIGNED` |
| 13 | `POST /admin/reports/{id}/resolve` ⚑ | Moderator | `{outcome:"dismissed"\|"action_taken", action?: {type, params}, note}` | **200** | `action` required when `action_taken`; note 10–1000 | 409 `REPORT_CLOSED` |
| 14 | `GET /admin/disputes` | Moderator | — | **200** Page with exchange, evidence, chat transcript link | — | — |
| 15 | `POST /admin/disputes/{id}/resolve` ⚑ | Moderator | `{resolution:"returned_ok"\|"owner_at_fault"\|"borrower_at_fault"\|"no_fault", trust_adjustments?, note}` | **200**; exchange closed; trust events written | Note required | 409 `DISPUTE_CLOSED` |
| 16 | `GET /admin/spam-signals` | Moderator | — | **200** Page of flagged entities `{entity, signal, score, evidence}` | — | — |
| 17 | `GET /admin/audit-logs` | Admin | — | **200** Page of `{actor, action, resource, ip, metadata, created_at}` (read-only) | `created_from` within 90 days unless archived export | 422 `RANGE_TOO_LARGE` |
| 18 | `GET /admin/stats/overview` | Admin | `window=7d\|30d\|90d` | **200** `{new_users, active_users, listings, exchanges_by_state, completion_rate, report_volume, avg_report_resolution_hours}` | — | — |

**List params**

- #1: filters `q` (email/name), `status`, `role`, `city_id`, `min_reports`, `created_from/to`; sort `-created_at`, `trust`, `-reports_count`; `include_total=true` allowed.
- #7: filters `status`, `owner_id`, `exchange_type`, `flagged`; sort `-created_at`.
- #10: filters `status`, `target_type`, `reason`, `assigned_to` (`me`), `sla_breached`; sort `created_at` (oldest first, default), `-priority`.
- #14: filters `status`, `reason`; sort `opened_at`.
- #16: filters `signal`, `min_score`; sort `-score`.
- #17: filters `actor_id`, `action`, `resource_type`, `resource_id`, `created_from/to`; sort `-created_at`.

---

## 12. Operational Endpoints

| Endpoint | Auth | Response |
| --- | --- | --- |
| `GET /health/live` | Public (internal network) | **200** process alive |
| `GET /health/ready` | Public (internal network) | **200**/**503** DB, Redis, migrations OK |
| `GET /openapi.json`, `GET /docs` | Public (disabled/protected in prod) | OpenAPI 3.1 schema |

---

## 13. Design Rationale (key decisions)

| Decision | Reason |
| --- | --- |
| **Action sub-resources for exchange transitions** | Each transition has distinct authorisation, validation, side-effects and audit. PATCHing `state` would force one endpoint to encode a state machine and weakens security |
| **Listing creation composes book + copy + offer** | The client thinks "I'm listing a book"; the server preserves the normalised book/copy/listing model internally |
| **`allowed_actions` in Exchange responses** | The server is the single source of truth for what is legal; the client stops duplicating rules |
| **Cursor pagination everywhere; offset nowhere** | Performance and consistency at millions of rows |
| **Search is GET with query params** | Cacheable, shareable URLs; filters are bounded so URLs stay short |
| **Idempotency keys on creation/transitions** | Mobile networks retry; double-requests must not double-reserve or double-message |
| **ETag + If-Match on mutable resources** | Prevents lost updates when two devices edit the same listing or profile |
| **404 instead of 403 for non-visible resources** | Does not reveal the existence of private clubs, chats or removed content |
| **Generic responses on forgot-password/resend/register (strict mode)** | Prevents account enumeration |
| **Signed direct uploads instead of multipart through the API** | Keeps large binaries off API servers; the API only ever handles `asset_id` references |
| **Chat has no "create conversation" endpoint** | Structurally enforces the product rule that chat requires an exchange |
| **WebSocket for delivery only, REST for truth** | Clients recover from drops via `after=` catch-up; the gateway scales independently |
| **Admin namespace `/admin` with separate role checks and mandatory audit** | Clear blast-radius boundary, easy to firewall and monitor |