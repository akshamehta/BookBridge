# 🏛️ Architecture Decision Record (ADR-001)

# Why BookBridge Uses a Modular Monolithic Architecture

**Status:** Accepted  
**Date:** October 2026

---

# Decision

BookBridge will be built using a **Modular Monolithic Architecture** instead of a Microservices Architecture.

The application will be deployed as a **single FastAPI application**, while internally separating the system into independent business modules such as Authentication, Books, Users, Exchange, Reviews, Notifications, and Reading Clubs.

This architecture provides a clean separation of concerns while keeping development, testing, and deployment simple.

---

# Problem Statement

BookBridge is intended to be a production-quality portfolio project that demonstrates software engineering principles rather than just CRUD functionality.

The architecture should:

- be easy to develop
- remain maintainable as features grow
- support future scalability
- demonstrate industry best practices
- avoid unnecessary complexity
- allow future migration to microservices

---

# Requirements

The architecture should satisfy the following goals.

## Functional Goals

- Authentication
- Book Management
- Book Exchange
- User Profiles
- Reviews
- Reading Clubs
- Notifications
- Wishlists
- Search
- Analytics
- Future AI Features

---

## Non-Functional Goals

- Clean architecture
- High maintainability
- Loose coupling
- Easy testing
- Fast development
- Production readiness
- Scalability
- Extensibility
- Simplicity

---

# Architectural Options Considered

## Option 1 — Traditional Monolith

```
Frontend

↓

Backend

↓

Database
```

### Advantages

- Very easy to build
- Simple deployment
- Fast development

### Disadvantages

- Business logic becomes tightly coupled
- Difficult to maintain as the project grows
- Poor separation of responsibilities
- Difficult for multiple developers to work simultaneously

---

## Option 2 — Microservices

```
User Service

Book Service

Exchange Service

Notification Service

Search Service

Recommendation Service
```

### Advantages

- Independent deployments
- Independent scaling
- Fault isolation
- Technology flexibility

### Disadvantages

- Considerably more infrastructure
- API Gateway required
- Service discovery
- Distributed transactions
- Increased operational complexity
- Harder local development
- Excessive complexity for an MVP

---

## Option 3 — Modular Monolith ✅ (Chosen)

```
                 FastAPI Application

┌────────────────────────────────────────────┐

 Authentication Module

 Users Module

 Books Module

 Exchange Module

 Search Module

 Notifications Module

 Reviews Module

 Reading Clubs Module

 Recommendation Module

 Admin Module

└────────────────────────────────────────────┘

           PostgreSQL

               +

             Redis
```

---

# Why Modular Monolith?

## 1. Separation of Business Domains

Each feature is developed as an independent module.

Instead of organizing code by technical layers,

```
controllers/
models/
routes/
services/
```

BookBridge is organized by business capability.

```
books/

users/

exchange/

reviews/

notifications/

clubs/
```

Every module owns its own

- routes
- services
- repositories
- schemas
- models

This significantly improves maintainability.

---

## 2. Faster Development

A single deployment means

- one backend
- one database
- one Docker container
- one CI/CD pipeline

Developers spend time building features rather than managing infrastructure.

---

## 3. Easier Debugging

With a single process,

stack traces remain straightforward.

No distributed tracing is required.

Errors are easier to reproduce and fix.

---

## 4. Simpler Local Development

Running the application requires only

- PostgreSQL
- Redis
- FastAPI

No service discovery.

No Kubernetes.

No API Gateway.

No message broker.

Developers can become productive quickly.

---

## 5. Lower Infrastructure Cost

Only one backend instance is required.

Ideal for

- MVPs
- startups
- student projects
- hackathons

Infrastructure remains simple while supporting production deployment.

---

## 6. Clear Boundaries

Although deployed together,

modules communicate through well-defined interfaces.

For example,

```
Exchange Module

↓

Notification Module
```

instead of accessing each other's database logic directly.

This encourages loose coupling.

---

## 7. Easier Testing

Each module can be tested independently.

Examples

```
Book Tests

Exchange Tests

Authentication Tests

Notification Tests
```

Integration tests remain straightforward because everything executes within one application.

---

## 8. Easier Refactoring

If requirements change,

modules can evolve independently.

The project remains organized even after adding dozens of features.

---

# Why Not Microservices?

Microservices solve organizational problems more than technical problems.

They become valuable when

- many engineering teams work simultaneously
- independent deployments are required
- different services experience different traffic patterns
- independent scaling is necessary

BookBridge does not currently face these challenges.

Using microservices now would introduce unnecessary complexity without providing meaningful benefits.

---

# Future Migration Strategy

The modular design intentionally prepares the system for future migration.

Current Architecture

```
                FastAPI

      ┌──────────┬──────────┬──────────┐

      Users     Books     Exchange

                Reviews

             Notifications
```

Future Architecture

```
Users Service

Books Service

Exchange Service

Notification Service

Recommendation Service

Search Service
```

Because each business domain is already isolated,

extracting a module into an independent service requires minimal code changes.

---

# Scalability

The modular monolith supports

- horizontal scaling
- Docker deployment
- load balancing
- Redis caching
- PostgreSQL replication
- CDN for static assets

The architecture can comfortably support significant user growth before microservices become necessary.

---

# Maintainability

Business logic is isolated.

Dependencies remain clear.

Developers know exactly where new features belong.

The project avoids becoming a "big ball of mud."

---

# Folder Structure

```
backend/

app/

├── auth/

├── users/

├── books/

├── exchange/

├── reviews/

├── notifications/

├── wishlist/

├── clubs/

├── recommendation/

├── common/

├── config/

├── database/

└── main.py
```

Each module contains

```
books/

book_controller.py

book_service.py

book_repository.py

book_model.py

book_schema.py

book_routes.py
```

This feature-based organization keeps related code together and improves discoverability.

---

# Architectural Principles

BookBridge follows these principles.

- Single Responsibility Principle
- Separation of Concerns
- Dependency Injection
- Layered Architecture
- Repository Pattern
- Service Layer Pattern
- Feature-Based Organization
- Domain-Oriented Design
- Clean Code Principles

---

# Trade-offs

| Benefit | Cost |
|----------|------|
| Simple deployment | Single deployment unit |
| Easy debugging | Entire application redeployed together |
| Lower operational complexity | Cannot independently scale individual modules |
| Easier testing | Shared runtime |
| Faster development | Larger executable over time |
| Lower infrastructure cost | Requires disciplined modular boundaries |

For the current stage of the project, these trade-offs are acceptable and align with the project's goals.

---

# Conclusion

A **Modular Monolithic Architecture** provides the best balance between simplicity, maintainability, scalability, and engineering quality for BookBridge.

It allows the application to remain easy to develop and deploy while encouraging strong modular boundaries and clean software design.

As the platform evolves, individual modules can be extracted into independent microservices without requiring a complete redesign of the system.

This approach reflects a pragmatic engineering philosophy:

> **Start simple, design for growth, and introduce complexity only when justified by real requirements.**
