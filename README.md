# BLG 483E HW2: Build Google with Multi-Agent AI

This project implements a single-machine web crawler and live search system for BLG 483E Homework 2. The crawler indexes pages from an origin URL up to depth `k`, prevents duplicate crawling, applies explicit back pressure, and keeps search available while indexing is still active. The implementation stays close to Python's standard library, using `urllib.request`, `html.parser`, `threading`, `queue.Queue`, `sqlite3`, and `http.server`.

HW2 extends the HW1 system with a documented multi-agent development workflow. The final runtime is still a normal localhost application, but the design and implementation process is described through separate agent roles, prompts, responsibilities, and review loops. See [multi_agent_workflow.md](multi_agent_workflow.md) and the files under [`agents/`](agents/).

## Deliverables

- Working crawler and search codebase
- [Product PRD](product_prd.md)
- [Production recommendation](recommendation.md)
- [Multi-agent workflow](multi_agent_workflow.md)
- Agent definition files in [`agents/`](agents/)

## Core Features

- `index(origin, k)` crawls reachable HTTP/HTTPS pages up to depth `k`
- `search(query)` returns triples shaped as `(relevant_url, origin_url, depth)`
- search can run while indexing is still active because pages commit incrementally into SQLite
- duplicate crawling is prevented globally through canonical URL storage and shared fetch coordination
- back pressure is enforced through a bounded in-memory queue and a shared rate limiter
- job progress, queue pressure, and event logs are exposed through a localhost dashboard
- interrupted jobs can be resumed from persisted frontier state

## Architecture Summary

```mermaid
flowchart LR
    UI["Dashboard / API"] --> INDEX["POST /api/index"]
    INDEX --> MANAGER["Crawler Manager"]
    MANAGER --> FRONTIER["SQLite Frontier"]
    MANAGER --> QUEUE["Bounded Work Queue"]
    QUEUE --> WORKERS["Worker Threads"]
    WORKERS --> FETCH["Fetch + Parse"]
    FETCH --> STORE["SQLite Pages / Terms / Links"]
    STORE --> SEARCH["GET /api/search"]
    SEARCH --> UI
```

### Multi-agent workflow at a glance

```mermaid
flowchart LR
    A["Architect"] --> B["Backend"]
    A --> C["Frontend"]
    B --> D["Reviewer"]
    C --> D
    D --> E["Documentation"]
    E --> H["Human Integrator"]
    D --> H
```

### Why search works during indexing

Workers commit each fetched page independently into SQLite. Because the database uses WAL mode, search requests can read fresh rows while new pages are still being inserted. This avoids end-of-job batch indexing and makes partial crawl results visible immediately.

### If search had to start independently while indexing was still booting

The current system already supports concurrent reads and writes after a crawl job exists. To make `search` safe even when indexing is just starting, the next production-oriented step would be to formalize visibility around committed page writes only. That means treating page ingestion as the source of truth, never reading from in-memory queues, and accepting that search is eventually consistent over the persisted store. In practice, the query path would continue reading from SQLite or a search index while indexers append newly committed pages asynchronously.

For a larger version of the same design, the crawler would keep frontier scheduling and fetch execution separate from the query path. Search would never block on crawl completion; it would simply return whatever postings have already been committed. A small freshness watermark or per-job "indexed through" timestamp would make that behavior explicit in the UI and API.

### Why this scales on one machine

The system separates durable crawl state from active in-memory work:

- the full frontier stays persisted in SQLite
- only a bounded slice is loaded into `queue.Queue`
- workers share a job-level rate limiter to control outbound request volume

This keeps memory growth controlled while allowing concurrent workers and resumable jobs.

## Project Layout

```text
.
|-- agents/
|-- crawler_app/
|   |-- http_server.py
|   |-- manager.py
|   |-- parser.py
|   |-- storage.py
|   `-- utils.py
|-- sample_site/
|-- static/
|-- tests/
|-- main.py
|-- product_prd.md
|-- recommendation.md
`-- multi_agent_workflow.md
```

## Run Locally

Python 3.12 is sufficient. No third-party runtime dependencies are required.

1. Start the sample site:

```bash
python -m http.server 9001 -d sample_site
```

2. Start the crawler dashboard:

```bash
python main.py --host 127.0.0.1 --port 3700 --auto-resume
```

By default the crawler persists state under `hw2/data/`. If you stop the process and restart it with the same `--data-dir`, resumable jobs and indexed pages remain available.

3. Open the dashboard:

```text
http://127.0.0.1:3700
```

4. Suggested demo configuration:

```text
Origin URL: http://127.0.0.1:9001/index.html
Max Depth: 2
Workers: 4
Rate Limit: 3
Queue Limit: 64
```

5. Suggested queries:

```text
python
crawler
concurrency
```

6. Optional CLI verification:

```bash
curl "http://127.0.0.1:3700/api/status"
curl "http://127.0.0.1:3700/api/search?q=python&limit=10"
```

## HTTP API

### Start a crawl

```http
POST /api/index
Content-Type: application/json

{
  "origin": "http://127.0.0.1:9001/index.html",
  "max_depth": 2,
  "worker_count": 4,
  "rate_limit": 3.0,
  "queue_limit": 64
}
```

### Search

```http
GET /api/search?q=python&limit=20
```

The handler also accepts `query` as an alias for `q`. Invalid numeric input such as `limit=abc` returns `400 Bad Request`.

### Observe state

```http
GET /api/status
GET /api/jobs
GET /api/jobs/{job_id}
POST /api/jobs/{job_id}/resume
```

## Grader-Friendly Verification Flows

### How to observe back pressure

1. Start the sample site and the dashboard.
2. Create a crawl job with:

```text
Origin URL: http://127.0.0.1:9001/index.html
Max Depth: 2
Workers: 1
Rate Limit: 20
Queue Limit: 1
```

3. Open the selected job card in the dashboard.
4. Watch `Queue Pressure` and `backpressure_events`.

Expected behavior:

- `in_memory_queue_depth` reaches the configured queue limit
- `backpressure_events` increases while the dispatcher waits for worker capacity
- the job still completes because excess frontier items remain durable in SQLite instead of being dropped

### How to verify resume

1. Start a crawl job from the sample site.
2. Stop the crawler process before the job finishes.
3. Restart the server with the same data directory and `--auto-resume`.
4. Open the dashboard or `GET /api/jobs/{job_id}` again.

Expected behavior:

- unfinished work is marked `resumable` on shutdown/boot
- restarting with `--auto-resume` continues from the persisted frontier
- already indexed pages are reused instead of being recrawled from scratch

## Data and persistence

- The default persistence directory is `hw2/data/`.
- SQLite files are created automatically on first run.
- Resume works only if the same data directory is reused across process restarts.
- Search reads directly from the persisted database, not from transient in-memory worker state.

## Testing

Run:

```bash
python -m unittest discover -s tests -v
```

The test suite verifies:

- crawl completion and indexed search results
- search visibility while indexing is still active
- resume behavior after interruption
- `max_depth = 0` behavior
- observable back pressure with a bounded queue
- invalid search-limit handling
- URL normalization edge cases used by deduplication

## Scope notes

- The runtime system is not a multi-agent runtime; the multi-agent requirement applies to the development workflow.
- The repository therefore includes explicit agent definitions, interaction rules, and a workflow document that describes how AI agents collaborate and how final decisions are made.
- The implementation still prioritizes native language features over external crawler frameworks, as required by the assignment.
- `robots.txt` support is intentionally left out of the runtime because the homework focuses on crawler architecture, deduplication, back pressure, and live search on localhost. The production recommendation explains how politeness controls would be added later.
