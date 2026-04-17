# HW2 Multi-Agent Workflow

## Objective

HW2 requires the crawler/search project to be completed through a multi-agent AI workflow. The runtime system itself is still a normal localhost crawler, but the development process is organized around specialized agents with explicit prompts, file ownership, review loops, and final human approval.

## Agent Set

The project uses five conceptual agents:

- `architect`: translates the assignment into a technical plan and keeps scope disciplined
- `backend`: owns crawler logic, storage, concurrency, and API behavior
- `frontend`: owns the dashboard and user-facing system state
- `reviewer`: audits correctness, assignment compliance, and testing gaps
- `documentation`: turns the implementation and agent collaboration into submission-ready deliverables

Each agent has a dedicated description file under [`agents/`](agents/).

## Why this split was chosen

The assignment is not only about building the crawler. It also asks the student to define agents, assign responsibilities, decide communication patterns, and evaluate outputs. The chosen split maps directly onto the natural seams in the project:

- architecture decisions had to be made before code changes
- crawler/search logic required concentrated backend ownership
- the dashboard needed separate attention to clarity and usability
- correctness and grading risk required an explicit review role
- documentation needed its own owner so the workflow itself would be visible in the repository

## Actual Collaboration Model

### 1. Architect stage

The architect agent starts from the assignment prompt and produces:

- the runtime scope
- the file set to reuse from HW1
- the list of artifacts to exclude
- the cleanup items required to make the project clearly an HW2 submission

Concrete architectural decisions made in this stage:

- reuse the proven single-machine crawler design from HW1
- keep SQLite WAL, bounded queue depth, and rate limiting
- keep the dashboard-based UX
- remove HW1-specific quiz compatibility code from the runtime
- add repository evidence for the multi-agent process through workflow and agent documents

### 2. Backend stage

The backend agent owns:

- crawl job creation and resumption
- dispatcher and worker coordination
- duplicate-fetch prevention
- persistent frontier and inverted index storage
- live search over committed pages

In this project, the backend work focused on turning the copied HW1 baseline into a clean HW2 core by removing quiz-only routes, score adapters, and flat-file export behavior that were no longer part of the homework brief.

### 3. Frontend stage

The frontend agent owns:

- updating the dashboard identity from HW1 to HW2
- keeping the page focused on assignment-required controls
- making queue pressure, worker activity, and search results understandable

The frontend contract is intentionally thin: it depends only on the JSON shapes returned by `/api/status`, `/api/jobs`, `/api/jobs/{job_id}`, `/api/index`, and `/api/search`.

### 4. Reviewer stage

The reviewer agent inspects the resulting project for:

- assignment compliance
- regressions caused by HW1 cleanup
- missing tests
- documentation gaps
- hidden grading risks

The reviewer does not approve the work alone. It produces findings or confirms that no substantial defects were found, after which the human integrator decides whether the submission is ready.

### 5. Documentation stage

The documentation agent produces:

- `README.md`
- `product_prd.md`
- `recommendation.md`
- `multi_agent_workflow.md`
- updated files under `agents/`

This agent is responsible for making the development process itself inspectable by course staff.

## Interaction and Handoff Rules

The workflow follows a strict handoff sequence:

1. `architect` defines the target behavior and boundaries.
2. `backend` implements the runtime logic against that contract.
3. `frontend` adapts the UI to the same contract.
4. `reviewer` inspects the result and raises issues.
5. `documentation` records the final system and workflow.
6. The human integrator resolves conflicts and makes the final submission decision.

Communication rules:

- agents communicate through concrete artifacts, not vague intent
- backend/frontend integration is based on explicit API fields
- the reviewer writes actionable findings, not generic comments
- the documentation agent must not invent behavior that the code does not implement

## Prompting Strategy

Each agent is given a constrained prompt tailored to one responsibility domain:

- the architect prompt emphasizes scope, assumptions, and ownership split
- the backend prompt emphasizes crawler correctness, deduplication, and back pressure
- the frontend prompt emphasizes clarity, not feature sprawl
- the reviewer prompt emphasizes defects, risks, and missing tests
- the documentation prompt emphasizes faithfulness to the implemented repository

The prompt templates are recorded in the individual agent files.

## Human Decision Points

The human integrator remains the final decision maker for:

- whether to reuse or discard HW1 components
- whether a feature is required by HW2 or just inherited noise
- whether review findings are blocking
- whether the deliverable set is complete enough to submit

This matters because the assignment explicitly says the student should design the system and make the final decisions, even if agents generate parts of the solution.

## Final Outcome

The resulting HW2 repository shows multi-agent collaboration in a concrete way:

- the runtime crawler/search system is implemented and validated
- the responsibilities of each agent are explicit
- the workflow and prompts are documented
- the final integration decisions remain human-owned

This satisfies the HW2 requirement that AI agents collaborate on the project without requiring the final crawler runtime itself to be a multi-agent system.
