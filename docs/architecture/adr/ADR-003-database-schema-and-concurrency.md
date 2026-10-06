# ADR-003: Database Schema, Indexing & Concurrency Control

**Status:** Accepted  
**Date:** October 2026  
**Deciders:** Lead Software Engineer & Quality Engineer  

---

## 1. Context & Problem Statement

In a collectible shoe marketplace, items are typically unique single-inventory physical pairs (e.g. Size 10.5 Jordan 1 Retro High Chicago in Near Deadstock condition).
Two critical engineering challenges arise:
1. **Concurrency Race Conditions:** If two buyers submit an order for the same exclusive listing at the exact same millisecond, the system must guarantee that exactly one order succeeds and the other receives an `INSUFFICIENT_STOCK` error (preventing double-selling).
2. **Search Performance:** Filtering across millions of listings by combinations of Brand, Model, Size, Condition, and Price range must execute in under 50ms.

---

## 2. Decision: Relational Schema with Concurrency Locks & pgvector

### 2.1 Core Entities

1. **`users`:** Identity, authentication (hashed password / OAuth), reputation score, profile metadata, soft-delete timestamp.
2. **`shoes`:** Master shoe catalog / reference model (Brand, Silhouette/Model, Release Year, SKU/Style Code, Original Retail Price).
3. **`listings`:** Individual physical pairs listed by sellers:
   - Foreign keys: `seller_id`, `shoe_id`.
   - Attributes: `size` (decimal), `condition` (`new`, `like_new`, `good`, `fair`), `price` (decimal, check > 0), `description`, `image_urls` (JSON array), `status` (`active`, `reserved`, `sold`, `delisted`).
   - AI metadata: `ai_condition_score` (float 0.0 - 1.0), `ai_verified_at` (timestamp), `embedding` (vector for semantic search).
4. **`orders`:** Transaction record connecting `buyer_id`, `listing_id`, `total_amount`, `currency`, `status` (`pending`, `paid`, `shipped`, `delivered`, `cancelled`), `idempotency_key` (UUID string), `created_at`.
5. **`audit_logs`:** Immutable record of status transitions for listings and orders.

### 2.2 Concurrency Control Pattern: Pessimistic Row-Level Locking

To guarantee zero double-buys:
```python
# Order checkout transaction
async with session.begin():
    # Acquire exclusive row-level lock on the listing
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .with_for_update()  # SELECT ... FOR UPDATE
    )
    result = await session.execute(stmt)
    listing = result.scalar_one_or_none()
    
    if not listing or listing.status != ListingStatus.ACTIVE:
        raise ListingNotAvailableException("Listing is no longer available.")
        
    # Transition status atomically
    listing.status = ListingStatus.RESERVED
    order = Order(
        buyer_id=buyer_id,
        listing_id=listing.id,
        amount=listing.price,
        status=OrderStatus.PENDING,
        idempotency_key=idempotency_key,
    )
    session.add(order)
```

### 2.3 Indexing Strategy

- **Composite index on active listings:** `CREATE INDEX idx_listings_active_brand_size ON listings (status, brand, size);`
- **Price sorting index:** `CREATE INDEX idx_listings_active_price ON listings (status, price);`
- **Unique index on idempotency:** `CREATE UNIQUE INDEX idx_orders_idempotency ON orders (idempotency_key);`
- **Vector index (HNSW):** `CREATE INDEX idx_listings_embedding ON listings USING hnsw (embedding vector_cosine_ops);`

---

## 3. Consequences

- **ACID Guarantees:** Ensures monetary and inventory transactions are safe under high concurrency.
- **Portability:** In SQLite local mode, standard transactions prevent concurrent writes via database-level serialization; in PostgreSQL production mode, row-level locks enable maximum concurrent transactions across different listings.
