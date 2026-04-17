# Product PRD: BLG 483E HW2 Multi-Agent Crawler

## 1. Goal

Build a localhost web crawler and search system that behaves like a simplified single-machine search engine. The system must crawl from an origin URL up to depth `k`, avoid crawling the same page twice, apply back pressure, expose search results as `(relevant_url, origin_url, depth)`, and support search while indexing is still active.

This project must also demonstrate a multi-agent AI development workflow. The final runtime does not need to execute agents, but the repository must clearly document the agents, their responsibilities, prompts, handoffs, and final human decision-making.

## 2. Users

- Course staff evaluating crawler correctness and architecture
- A developer running the project locally on one machine
- An AI-assisted implementation workflow that needs explicit build instructions

## 3. Functional Requirements

### 3.1 Index

- Input: `origin`, `k`
- Crawl only valid HTTP/HTTPS URLs reachable from `origin`
- Interpret depth as hop count from the origin
- Never crawl the same page twice within the persisted system state
- Enforce bounded work using queue depth and/or request rate limiting
- Persist enough state to observe progress and optionally resume jobs

### 3.2 Search

- Input: `query`
- Return a list of triples shaped as `(relevant_url, origin_url, depth)`
- Surface new results while indexing is still in progress
- Use a simple, explainable ranking strategy

### 3.3 Local Operation

- Provide a simple localhost UI or CLI for:
  - starting crawl jobs
  - searching indexed content
  - viewing runtime state such as queue depth, active workers, and job status

## 4. Non-Functional Requirements

- Prefer Python standard-library components over fully featured crawler frameworks
- Design for large crawls on a single machine, not distributed infrastructure
- Keep the system easy to inspect and reason about
- Make operational state visible enough for grading and debugging

## 5. Proposed Technical Design

### 5.1 Runtime

- `urllib.request` for HTTP fetching
- `html.parser` for extracting title, visible text, and links
- `sqlite3` in WAL mode for persistent frontier, page store, and inverted index
- `threading` plus `queue.Queue` for dispatcher/worker coordination
- `http.server` for the dashboard and JSON API

### 5.2 Search While Indexing

- Commit each page independently into SQLite
- Execute search directly against committed rows
- Use WAL mode so reads remain available during writes

### 5.3 Back Pressure

- Keep the frontier durable in SQLite
- Load only a bounded number of items into the in-memory queue
- Rate-limit outgoing requests at the job level

### 5.4 Deduplication

- Normalize URLs before inserting them into the frontier
- Store canonical pages globally
- Coordinate concurrent fetches so only one thread retrieves a new URL

## 6. Multi-Agent Workflow Requirements

The repository must include:

- a workflow document explaining the agent structure
- separate agent description files
- prompts and responsibility boundaries for each agent
- a description of how conflicts are resolved and how humans make final decisions

Suggested agents:

- architect
- backend
- frontend
- reviewer
- documentation

## 7. Acceptance Criteria

- A crawl can be started from a localhost URL
- Search returns `(relevant_url, origin_url, depth)` tuples
- Search works before the job is fully complete
- The crawler does not refetch the same canonical page unnecessarily
- Runtime back pressure is visible through queue/rate signals
- The dashboard shows job progress and events
- The repository includes `README.md`, `product_prd.md`, `recommendation.md`, `multi_agent_workflow.md`, and `agents/`
- The code runs locally without third-party runtime dependencies

## 8. Out of Scope

- Distributed crawling across multiple machines
- Advanced ranking such as PageRank or semantic retrieval
- JavaScript rendering
- Robots.txt enforcement and host-level politeness scheduling beyond the basic homework scope
