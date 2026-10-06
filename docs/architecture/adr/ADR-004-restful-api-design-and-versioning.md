# ADR-004: RESTful API Design & Versioning

**Status:** Accepted  
**Date:** October 2026  
**Deciders:** Lead Software Engineer & Quality Engineer  

---

## 1. Context & Problem Statement

The API must serve web applications, future mobile apps (e.g. React Native), and automated testing suites. It must follow clear RESTful conventions, provide uniform response contracts, handle pagination gracefully, and avoid breaking backward compatibility as new features (e.g., AI assistants) are introduced.

---

## 2. Decision: Versioned RESTful API with Envelope Contracts

### 2.1 URL Path Versioning
All API endpoints are versioned explicitly via URL prefix:
`/api/v1/...`

### 2.2 Standard Success Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_count": 142,
    "total_pages": 8
  },
  "request_id": "req_01h8a3e7b4"
}
```

### 2.3 Core Endpoints

#### Authentication & Users
- `POST /api/v1/auth/register` - Create account with email & password
- `POST /api/v1/auth/login` - Authenticate & obtain JWT access + refresh tokens
- `POST /api/v1/auth/refresh` - Refresh expired access token
- `GET  /api/v1/users/me` - Get authenticated profile
- `PUT  /api/v1/users/me` - Update profile details

#### Shoe Catalog & Listings
- `GET    /api/v1/listings` - List active listings with multi-attribute filtering & cursor/offset pagination
- `POST   /api/v1/listings` - Create new listing (Authenticated seller)
- `GET    /api/v1/listings/{id}` - Retrieve listing details
- `PUT    /api/v1/listings/{id}` - Update listing price / details (Owner only)
- `DELETE /api/v1/listings/{id}` - Soft-delete or delist (Owner only)

#### Orders & Checkout
- `POST /api/v1/orders` - Place order on a listing (atomic row-lock checkout with idempotency key)
- `GET  /api/v1/orders` - View buyer's order history
- `GET  /api/v1/orders/{id}` - View order details & status

#### AI & Intelligence Services
- `POST /api/v1/ai/assess-condition` - Multimodal image upload analyzing shoe condition & brand
- `POST /api/v1/ai/price-estimate` - Historical comp analysis & price recommendation
- `GET  /api/v1/ai/semantic-search` - Natural language query matching using embeddings

---

## 3. Benefits for Testing & Clients

- Automated OpenAPI 3.1 documentation available at `/docs` (Swagger UI) and `/redoc`.
- Predictable JSON shapes simplify frontend TypeScript type generation.
- Automated API contract testing with `pytest` ensures schema integrity across releases.
