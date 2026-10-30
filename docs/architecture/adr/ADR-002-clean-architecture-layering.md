# ADR-002: Clean Architecture & Layering Pattern

**Status:** Accepted  
**Date:** October 2026  

---

## 1. Context & Problem Statement

Marketplace backends frequently degenerate into "fat controllers" or tightly coupled database queries inside route handlers. This makes automated testing slow, makes switching data backends difficult, and obscures business logic behind HTTP concerns.

To showcase strong backend engineering practices, the architecture will maintain strict separation of concerns, testability in isolation, and dependency inversion.

---

## 2. Decision: 4-Layer Architecture

We adopt a Clean / Hexagonal-inspired layered architecture:

```mermaid
flowchart TD
    subgraph Presentation ["1. Presentation Layer (API / Handlers)"]
        Routes["FastAPI Routers & Endpoints"]
        Middleware["Security, Rate Limiting, Request ID"]
        Schemas["Pydantic Request & Response DTOs"]
    end

    subgraph Application ["2. Application Layer (Services)"]    
        ListingService["ListingService (validation, business rules)"]
        OrderService["OrderService (checkout, state transitions)"]
        AuthService["AuthService (JWT, password verification)"]
        AIService["AIService (condition grading, embeddings)"]
    end

    subgraph Domain ["3. Domain Layer"]
        Entities["SQLAlchemy ORM Entities"]
        DomainEnums["Enums (ShoeCondition, OrderStatus)"]
        DomainExceptions["DomainException, InsufficientStockException"]
    end

    subgraph Infrastructure ["4. Infrastructure & Data Access"]
        Repos["Async Repositories (ListingRepository, OrderRepository)"]
        DBEngine["SQLAlchemy Async Engine & Sessions"]
        CacheClient["Redis / Memory Cache Adapter"]
        ExternalAI["Google Gemini Client"]
    end

    Routes --> Schemas
    Routes --> Application
    Application --> Domain
    Application --> Repos
    Application --> CacheClient
    Application --> ExternalAI
    Repos --> DBEngine
    Repos --> Entities
```

### Layer Responsibilities:

1. **Presentation Layer (`app/api/`):**
   - Validates incoming HTTP payloads via Pydantic schemas.
   - Extracts authorization tokens and request contexts.
   - Injects services via FastAPI's `Depends()`.
   - Never calls database sessions directly; strictly delegates to services.
2. **Service / Business Logic Layer (`app/services/`):**
   - Implements core business logic: e.g., "A seller cannot purchase their own listing", "An order cannot transition to PAID if listing is no longer ACTIVE".
   - Coordinates between repositories, caching, and AI engines.
   - Manages atomic transactions and triggers cache invalidations.
3. **Domain Layer (`app/domain/`):**
   - Pure domain models, database entity definitions, status enums, and domain exception classes.
4. **Data Access / Repository Layer (`app/repositories/`):**
   - Encapsulates all SQL queries, pagination logic, vector similarity queries, and database locks (`with_for_update`).
   - Returns typed domain models to the service layer.

---

## 3. Benefits for Testing & Maintainability

- **Unit Testing:** Services can be tested in sub-millisecond unit tests by passing mock repositories without hitting a real database.
- **Integration Testing:** Repositories and endpoints can be tested with real database rollbacks.
- **Portability:** Switching underlying databases or cache backends requires zero changes to the business logic layer.
