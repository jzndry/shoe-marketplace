# ADR-008: AI Multimodal & Semantic Search Architecture

**Status:** Accepted  
**Date:** October 2026  
**Deciders:** Lead Software Engineer & Quality Engineer  

---

## 1. Context & Problem Statement

Artificial Intelligence in modern web marketplaces must provide concrete business utility rather than superficial novelty. For a sneaker marketplace, three key user friction points exist:
1. **Seller Listing Friction & Inaccurate Grading:** Sellers struggle to write descriptions and often misjudge shoe condition (e.g. labeling worn shoes as "Like New").
2. **Buyer Discovery Friction:** Buyers frequently describe what they want in natural language (e.g., "vintage high top basketball sneakers with retro red colorway for under $150") rather than using rigid relational filter dropdowns.
3. **Pricing Uncertainty:** Sellers don't know the fair market value of their used shoes.

---

## 2. Decision: Google Gemini Multimodal Vision + pgvector Embeddings

### 2.1 AI Service Modules

1. **Multimodal Condition & Silhouette Classifier:**
   - **Model:** Google Gemini (`gemini-1.5-flash` / `gemini-2.5-flash`).
   - **Input:** 1 to 4 uploaded images (upper, outsoles, heel counter, box label).
   - **Output:** Structured JSON schema via Gemini structured outputs:
     - `brand` (e.g. Nike, Jordan, Adidas, New Balance)
     - `silhouette` (e.g. Air Jordan 1 Retro High OG)
     - `colorway` (e.g. Chicago, Lost & Found)
     - `condition_grade` (`Deadstock`, `Near Deadstock`, `Good`, `Fair`)
     - `wear_indicators` (creasing, heel drag, star loss, box condition)
     - `suggested_title` & `suggested_description`
2. **Hybrid & Semantic Vector Search:**
   - **Model:** `text-embedding-004` (768 dimensions).
   - Listings generate combined text vectors (Brand + Model + Colorway + Description) indexed with HNSW in PostgreSQL via `pgvector`.
   - Buyer search queries are embedded and compared using cosine distance (`<=>`), combined with SQL `WHERE` clauses for hard filters (e.g., `size = 10.5 AND price <= 150`).
3. **Dynamic Market Price Estimator:**
   - Evaluates recent completed orders for the same silhouette and condition grade, computing 25th percentile (fast sale), 50th percentile (fair market), and 75th percentile price points.

### 2.2 Graceful Degradation & Mock Fallback Strategy

To ensure that the application builds, runs, and tests reliably even when external API keys or network connectivity to Google Gemini are not present:
- The `AIService` implements a mock fallback provider (`MockAIService`) used during automated testing and offline development.
- In offline mode, heuristic rule-based classifiers and synthetic vector generators provide deterministic test responses, preventing test flakiness in CI pipelines.
