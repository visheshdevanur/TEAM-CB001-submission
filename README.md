# MysuruDrishti — Evidence-based civic follow-through for Mysuru

> HackMysuru 1.0 · Phase 1 · Civic Governance & Clean Mysuru
> Team `Code Breakers` (`CB001`)

| 📎 Submission links | 📋 Templates | 🏗️ Architecture | 🛡️ Hard constraints | ⚙️ Setup | 🤖 AI usage | ⚠️ Limitations |
|---|---|---|---|---|---|---|
| [resource.md](./resource.md) | [resource-templates/](./resource-templates/) | [docs/architecture.md](./docs/architecture.md) | [docs/constraints.md](./docs/constraints.md) | [docs/setup.md](./docs/setup.md) | [ai.md](./ai.md) | [docs/limitations.md](./docs/limitations.md) |

<!--
This README is the overview. Detailed content lives in the linked files so each stays short.
Keep the section ORDER below. Reviewers look for each section in the same place in every repo.
-->

---

## 1. Problem Understanding

<!-- Which sub-problem did you pick and WHY that one? 5–8 sentences. -->

**Chosen sub-problem:** `Follow-through, verification, and field-worker feedback`

- **The gap we saw:** A complaint may be filed but citizens cannot reliably see who owns it, whether a field worker responded, or whether the visible issue was actually fixed.
- **Why it matters:** Delayed acknowledgement and unverified closure reduce public trust and allow civic hazards to remain unresolved.
- **Why we chose this over the others:** We focused on the hand-off from report to worker action because it connects the citizen, field worker, and MCC in one measurable workflow.
- **What "solved" looks like for us:** A location-selected complaint is routed to an allotted worker, acknowledged, supplied with After evidence, and visible to the citizen and MCC with an AI-supported review.

## 2. Target Users & Mysuru Context

| User | Their situation | What they need from us |
|---|---|---|
| Mysuru resident | Needs a simple way to report an issue at the real location | Submit a category, map point, address, and Before photo; see the status later |
| MCC administrator | Needs visibility of assignments and stalled reports | Allot worker areas, see live status, identify assignments unacknowledged after 3 days |
| Field worker | Needs only the complaints in the allotted service area | Acknowledge work, add an After photo, and see the verification result |

**Local context we designed for:** Mysuru map bounds, location-permission fallback through map selection, address lookup, and visible worker follow-through.

## 3. Solution Overview

<!-- Plain language. A non-engineer should follow this. -->

Public users create map-based civic reports with Before evidence. MCC administrators draw non-overlapping worker areas on a Mysuru map, which routes matching reports to a worker. The worker acknowledges and completes work with an After photo; Gemini reviews category and visual Before/After evidence, while MCC and the resident can inspect the result.

**Core flow:**
1. `A citizen selects an exact map location, confirms the address, and uploads a Before photo.`
2. `The backend finds the allotted worker polygon containing that location.`
3. `The worker acknowledges the assignment and uploads an After photo.`
4. `Gemini returns a visual result and score, visible to the citizen, worker, and MCC.`

**Screenshots:** `<2–4 images under docs/images/, each < 1 MB>`

## 4. Architecture

`React client → FastAPI REST API → PostgreSQL, with polygon-based worker routing and Gemini visual verification.`

➡️ Diagram, components, data model and APIs: **[docs/architecture.md](./docs/architecture.md)**

## 5. Tech Stack & AI Usage

**Stack:** `React + TypeScript · FastAPI · PostgreSQL · Leaflet/OpenStreetMap · Gemini API` (full rationale in [docs/architecture.md](./docs/architecture.md#tech-stack))

**AI tools used in development:** `OpenAI Codex`
**AI inside the product:** `Google Gemini visual review`

➡️ Full disclosure: **[ai.md](./ai.md)**

## 6. Decision Log (Summary)

<!-- The full 1-page Decision Log is a PDF on Google Drive, linked in resource.md. ≤ 3 lines here. -->

- **Chose:** polygon-based area allocation and explicit worker acknowledgement, **over:** static north/central/south labels.
- **Because:** map boundaries make the assignment rule visible and directly testable, at the cost of requiring MCC setup.
- **First thing to break at city scale:** application-side polygon scans; migrate to PostGIS spatial indexes.

➡️ Full decision log: **[resource.md](./resource.md#4-submission-artifacts-google-drive)** · Template: **[decision-log-template.md](./resource-templates/decision-log-template.md)**

## 7. Setup & Run

```bash
git clone https://github.com/visheshdevanur/TEAM-CB001-submission.git && cd TEAM-CB001-submission/src
cd frontend && npm install && npm run dev
```

➡️ Prerequisites, environment variables, seed data and offline testing: **[docs/setup.md](./docs/setup.md)**

## 8. Known Limitations

- The MVP needs an active network connection; offline queueing is planned but not implemented.
- Gemini API quota or availability can delay a visual result; the app shows that the assessment is unavailable rather than fabricating a score.
- Worker-area boundaries are manually drawn MCC allocation zones, not official government GIS boundaries.
- Device location and address lookup depend on browser permissions and third-party mapping services.
- City-scale routing needs spatial indexes and stronger audit/security controls.

### Future Implementation Plan

| Current limitation | Planned solution |
|---|---|
| Internet is required to file a complaint | Add a PWA offline queue that saves the report, images, and selected location locally, then retries securely when the device reconnects. |
| GPS permissions or accuracy can be limited | Keep manual map placement, add a clearer accuracy indicator, and let the resident adjust the pin before submission. |
| Manually drawn service areas are approximate | Import verified MCC/KGIS ward and service-boundary data, with versioned boundary updates and an escalation queue for border cases. |
| Gemini can be unavailable or receive unclear evidence | Add retry/backoff handling, photo-quality checks before upload, a status message for the user, and an MCC escalation queue for unavailable assessments. |
| Images are stored with application data | Move evidence files to private object storage with signed access URLs, retention rules, compression, and deletion controls. |
| Application-side routing will not scale indefinitely | Use PostGIS geography indexes for point-in-polygon queries, background queues for AI assessments, audit trails, and role-based access controls. |

➡️ Full list, edge cases and scaling roadmap: **[docs/limitations.md](./docs/limitations.md)**

---

## Team

| Name | Role | GitHub |
|---|---|---|
| Bhavish S | Team lead & integration | [@Bhavish-S](https://github.com/Bhavish-S) |
| Yashavanth B N | Product & testing | [@bnyashavanth-prog](https://github.com/bnyashavanth-prog) |
| Varshith V | Backend & worker workflow | [@4mh24cs167-tech](https://github.com/4mh24cs167-tech) |
| Vishesh G Devanur | Frontend & AI integration | [@visheshdevanur](https://github.com/visheshdevanur) |

## License

`<MIT / Apache-2.0 / None>`. You retain full ownership of your code.
