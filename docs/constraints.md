# The Five Hard Constraints

[← Back to README](../README.md)

> Status is deliberately honest: ✅ handled in the MVP · ⚠️ partially handled · ❌ not implemented. Video references below use the final recorded chapter ranges.

| # | Constraint | Status | Video |
|---|---|---|---|
| 1 | Fake, spam and harassment reports | ⚠️ Partial | `08:05–08:32` — Scale, limitations, and AI disclosure |
| 2 | Unclear jurisdiction | ⚠️ Partial | `01:17–02:21` — MCC administrator dashboard and worker-area allocation |
| 3 | Prioritisation beyond "most votes" | ❌ Not implemented | `07:28–08:04` — Decision and trade-offs |
| 4 | Bad input: duplicate, fake photo, wrong location, abuse | ⚠️ Partial | `03:30–04:25` — AI result and notifications |
| 5 | Works without internet | ❌ Not implemented | `08:05–08:32` — Scale, limitations, and AI disclosure |

---

## 1. Fake, spam and harassment reports

- **Approach:** Public users must sign in before filing and evidence is tied to the reporter's account. MCC can see complaint status and worker assignment rather than accepting anonymous closures.
- **Current limitation:** There is no rate limit, abuse classifier, reporter reputation system, or content-moderation queue yet.
- **Code:** `src/backend/app/api/routes/auth.py`, `src/backend/app/api/routes/complaints.py`

## 2. Unclear jurisdiction

- **Approach:** MCC draws a named, non-overlapping polygon for each worker. A complaint is assigned only when its selected point lies inside that polygon.
- **What happens in a boundary/outside case:** The complaint remains `UNASSIGNED` for MCC review. MCC can draw, change, or remove an allocation; saving an area backfills older unassigned reports inside it.
- **Current limitation:** These are manually created allocation zones, not official MCC/KGIS boundaries.
- **Code:** `src/backend/app/api/routes/areas.py`

## 3. Prioritisation

- **Current MVP behavior:** The MCC dashboard shows live totals, verification outcomes, recurring-location count, and reports that have not been acknowledged by a worker after three days.
- **Why not simply "most votes":** The MVP does not use vote counts or claim to have a production priority formula. A future formula should combine severity, age, recurrence, sensitive-location impact, and service-level breach.
- **Code:** `src/backend/app/api/routes/complaints.py`

## 4. Bad input

| Input | What the MVP does |
|---|---|
| Duplicate report | No automatic duplicate merge yet; MCC can see recurring location counts. |
| Fake / unrelated photo | Gemini checks category and Before/After evidence when an After photo is uploaded. A category mismatch or unclear result does not produce a fabricated resolution score. |
| Wrong or impossible location | The resident can place or adjust a map pin; reverse geocoding fills the address. Device location is optional because permissions and GPS may fail. |
| Abusive message | Basic complaint data is stored, but there is no automated text moderation yet. |
| Oversized upload | Evidence upload rejects files larger than 25 MB. |

## 5. Offline operation

- **What works offline:** No end-to-end complaint workflow is supported offline.
- **What does not work offline:** Authentication, map tiles/geocoding, uploads, PostgreSQL API calls, notifications, and Gemini assessment all require connectivity.
- **Future approach:** Add a PWA queue, local encrypted draft storage, background sync, offline map packs, and an on-device or locally hosted visual model where appropriate.
- **How to test the real MVP:** Keep the device online; see [setup.md](./setup.md).
