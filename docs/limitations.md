# Known Limitations & Future Scope

[← Back to README](../README.md)

## What Doesn't Work Yet

| Limitation | Why it exists | What we'd do next |
|---|---|---|
| Offline complaint submission and automatic sync | The MVP depends on live API, map, upload, and Gemini services. | Add a PWA queue, encrypted local drafts, background sync, offline map packs, and a locally hosted/on-device visual model where feasible. |
| Worker boundaries are manually drawn | Official MCC/KGIS allocation data was not integrated in the hackathon MVP. | Import verified GIS boundaries, version them, and add an MCC escalation queue for border cases. |
| Gemini can be unavailable or assess unclear evidence poorly | The visual model depends on external availability, quota, network, and image quality. | Add upload-quality feedback, retry/backoff, usage monitoring, and a review queue for unresolved assessments. |
| Evidence files are stored with application data | It is a practical MVP choice, not a city-scale media architecture. | Move images to private object storage with signed URLs, lifecycle retention, backups, and deletion controls. |
| No automated spam, duplicate, or abuse moderation | The MVP focuses on reporting, routing, evidence, and result visibility. | Add rate limits, duplicate detection, moderation, and audit tools. |

## Edge Cases We Don't Handle Fully

- GPS spoofing or an inaccurate device location that the resident does not correct on the map.
- A complaint on or near a manually drawn area edge.
- Several workers needing overlapping responsibility for one location.
- Before and After images taken from very different viewpoints, lighting, or times.
- Repeated malicious reports or abusive descriptions without manual MCC intervention.

## Scaling to All of Mysuru

| What breaks first | Rough numbers | Fix |
|---|---|---|
| Application-side scan of all worker polygons for each new complaint | As worker areas grow into the hundreds or thousands, per-request scans become slower and harder to audit. | Store polygons in PostGIS and use a spatial index for point-in-polygon queries. |
| Synchronous external visual assessments | A surge of After-photo uploads can hit Gemini quota or increase waiting time. | Use a durable background queue, retry policy, rate limit, and monitoring dashboard. |
| Evidence stored in the relational database | Image storage and backups grow much faster than complaint metadata. | Use private object storage with CDN delivery and retention policies. |

## Roadmap

1. Pilot the workflow with one MCC service team using verified service-area data and measured response-time targets.
2. Add Kannada-first guidance, accessibility improvements, and offline complaint drafts for low-connectivity use.
3. Add official GIS boundaries, PostGIS routing, moderation/duplicate detection, object storage, and queued AI assessment for city-scale rollout.
