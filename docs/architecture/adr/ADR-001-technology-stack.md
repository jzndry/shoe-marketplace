# ADR-001: Technology Stack Selection

**Status:** Accepted  
**Date:** October 2026  
**Deciders:** Lead Software Engineer & Quality Engineer  

---

## 1. Context & Problem Statement

The goal is to design a production-grade shoe marketplace ("SoleMarket") that showcases advanced backend software engineering, robust quality assurance automation (QAT/SDET), and practical artificial intelligence integration. 

We need a technology stack that satisfies four primary criteria:
1. **Asynchronous, High-Throughput Backend:** Capability to handle concurrent requests, inventory locks, and non-blocking I/O for database, cache, and external AI services.
2. **Native AI Ecosystem:** Frictionless integration with multimodal LLMs (e.g., Google Gemini), vector search, and image processing without cross-process IPC bottlenecks.
3. **Robust Quality Assurance & Automation:** A testing ecosystem that supports unit tests, integration tests with database rollbacks, load testing, and browser automation via Selenium WebDriver.
4. **Strong Frontend Typing & State Management:** Modern TypeScript frontend with decoupled state management for deterministic UI testing.

---

## 2. Considered Alternatives

### Backend Options:
- **Option 1: FastAPI (Python 3.9+) [Selected]**
  - *Pros:* Native `async/await` ASGI architecture; runtime schema validation with Pydantic v2; auto-generated OpenAPI 3.1 documentation; direct access to the entire Python AI ecosystem (Google Generative AI, PyTorch, NumPy); world-class testing tooling (`pytest`, `pytest-asyncio`, `httpx`).
  - *Cons:* Slower raw CPU performance compared to compiled Go, mitigated through async I/O and caching.
- **Option 2: Go (Gin / Fiber)**
  - *Pros:* Exceptional concurrency through goroutines, minimal memory footprint, single binary deployment.
  - *Cons:* Lack of direct SDKs for advanced AI pipelines; requires running Python sidecar microservices or gRPC wrappers for AI inference.
- **Option 3: Django + Django REST Framework**
  - *Pros:* Rich built-in admin panel and ORM.
  - *Cons:* Historically synchronous; async ORM is less ergonomic; heavier abstraction layers hide low-level architectural patterns.

### Frontend Options:
- **Option 1: Vite + React 19 + TypeScript + Tailwind CSS [Selected]**
  - *Pros:* Extremely fast build times; completely decoupled Single Page Application (SPA); predictable DOM element locators suitable for Selenium Page Object Model (POM); state management via TanStack Query.
  - *Cons:* Client-side rendering requires handling loading states explicitly (which actually benefits E2E testing).
- **Option 2: Next.js (Fullstack App Router)**
  - *Cons:* Blurs the boundary between client and server; makes standalone backend API showcasing less isolated.

### Database & Caching:
- **PostgreSQL 16 + pgvector:** ACID compliance, row-level locking (`SELECT ... FOR UPDATE`), native relational indexing, and vector similarity search. (With SQLite + aiosqlite as zero-dependency dev/test fallback).
- **Redis 7:** Read-through cache, token-bucket rate limiter, and idempotency store. (With thread-safe memory fallback for isolated testing).

---

## 3. Decision Outcome

We decided on:
- **Backend:** **FastAPI (Python) + SQLAlchemy 2.0 (Async) + Alembic + Pydantic v2**
- **Frontend:** **Vite + React 19 + TypeScript + Tailwind CSS + TanStack Query**
- **Data & Cache:** **PostgreSQL 16 (pgvector) + Redis 7** (with graceful SQLite/In-memory local fallback)
- **Testing & QA:** **Pytest + Selenium WebDriver (Python) with Page Object Model + Locust**
- **AI Engine:** **Google Gemini API (multimodal vision + text embeddings)**

---

## 4. Consequences & Trade-offs

- **Positive:**
  - Python unifies both the backend API and AI intelligence pipelines in a single, high-performing asynchronous codebase.
  - Tests can be written using Python's ecosystem (`pytest` for backend, `selenium` for frontend E2E), allowing shared fixtures and test utilities.
  - Decoupled REST API ensures the backend can be consumed by any client (web, mobile, third-party partners).
- **Negative:**
  - Requires diligent async programming practices (avoiding blocking synchronous calls within async event loops).
