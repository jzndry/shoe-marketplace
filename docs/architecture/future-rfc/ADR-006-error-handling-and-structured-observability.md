# ADR-006: Error Handling, Exception Hierarchy & Structured Observability

**Status:** Accepted  
**Date:** October 2026  
**Deciders:** Lead Software Engineer & Quality Engineer  

---

## 1. Context & Problem Statement

Uncaught exceptions or generic `500 Internal Server Error` strings provide bad user experiences and make root cause analysis difficult in production. Automated tests also need deterministic error codes (`LISTING_NOT_FOUND`, `INSUFFICIENT_STOCK`, `UNAUTHORIZED`) to assert behavior without parsing raw strings.

---

## 2. Decision: Domain Exception Hierarchy & Centralized Middleware

### 2.1 Standardized Error Envelope
All error responses return the following JSON structure:
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "The requested shoe listing has already been reserved or sold.",
    "status_code": 409,
    "details": {
      "listing_id": 42,
      "current_status": "sold"
    },
    "request_id": "req_01h8a3e7b4",
    "timestamp": "2026-10-07T00:46:00Z"
  }
}
```

### 2.2 Exception Hierarchy in Python
```python
class AppException(Exception):
    """Base application exception."""
    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ResourceNotFoundException(AppException):
    status_code = 404
    code = "RESOURCE_NOT_FOUND"

class InsufficientStockException(AppException):
    status_code = 409
    code = "INSUFFICIENT_STOCK"

class UnauthorizedException(AppException):
    status_code = 401
    code = "UNAUTHORIZED"

class ForbiddenException(AppException):
    status_code = 403
    code = "FORBIDDEN"

class ValidationException(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"
```

### 2.3 Structured Observability Middleware
- Every incoming request is assigned a unique UUID `X-Request-ID` via middleware.
- Structured JSON logging captures:
  - `timestamp`, `level`, `request_id`, `method`, `path`, `status_code`, `latency_ms`, and `user_id`.
- Correlation ID is propagated to frontend error responses so user bug reports can be instantly matched with server logs.
