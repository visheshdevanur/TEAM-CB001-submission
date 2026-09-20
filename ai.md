# AI Usage Disclosure

[← Back to README](./README.md)

> AI tools are **100% permitted** at HackMysuru 1.0. Disclosing them is **mandatory**.
> Using AI never costs you points. Not being able to explain code you submitted does.
> Reviewers check this file against your commit history and the AI segment of your video.

<!--
This file covers two different things. Keep them separate:
  Section 1: AI tools YOU used while building (ChatGPT, Copilot, Cursor, Claude, v0, ...)
  Section 3: AI models your PRODUCT uses at runtime (vision model, LLM classifier, ...)
If you used no AI at all, say so explicitly in the Summary and delete the rest.
-->

---

## Summary

| Question | Answer |
|---|---|
| Did we use AI tools during development? | `Yes` |
| Does our product use AI/ML at runtime? | `Yes` |
| Roughly how much of the code was AI-assisted? | `Approximately 70% overall` |
| Can every team member explain the AI-assisted code? | `Yes` |

---

## 1. AI Tools Used During Development

| Tool | Model / plan | Used by | What we used it for |
|---|---|---|---|
| `OpenAI Codex` | `Codex coding agent` | `All team members` | `UI implementation, backend/API integration, debugging, deployment troubleshooting, documentation, and test support.` |
| `ChatGPT` | `ChatGPT` | `All team members` | `Requirement clarification, workflow design, technical explanation, and review of implementation options.` |

## 2. Where AI Helped in the Codebase

| Area / file | Level of AI help | What a human did |
|---|---|---|
| `src/frontend/` | `High` | `Team members set the product flow, checked UI behavior, tested role-specific dashboards, and corrected integration issues.` |
| `src/backend/app/` | `Medium to high` | `Team members configured deployment, verified API behavior, environment variables, authentication, and database-backed workflows.` |
| `Worker-area routing and operational rules` | `Medium` | `The team chose the polygon-allocation workflow, reviewed the routing behavior, and tested it using Mysuru locations.` |
| `README.md, resource.md, and docs/` | `High` | `The team supplied factual project details, reviewed claims, and approved the final documentation.` |

**Commit convention (optional, recommended):** commits containing substantial AI-generated code are tagged `[ai]` in the message, e.g. `feat: ward status page [ai]`.

## 3. AI Inside the Product (runtime)

<!-- Delete this section if your product uses no AI/ML at runtime. -->

| Model / API | What it does in our product | Hosted where | Trained / fine-tuned by us? |
|---|---|---|---|
| `Google Gemini API` | `Reviews the selected complaint category with the Before and After evidence images, then returns a score and outcome explaining whether the visible issue appears resolved.` | `Google Gemini API, called by the FastAPI backend` | `No; prompt-based use of the provider model.` |

- **Accuracy we measured:** `Not formally measured yet. The MVP was manually tested using representative Before/After complaint images.`
- **What happens when the model is wrong:** `The score is shown with Gemini's evidence explanation. If assessment is unavailable, unclear, or category-mismatched, the application does not fabricate a score and asks for clearer/new evidence.`
- **Does it work offline?** `No. Gemini assessment requires an internet connection and an available API.`
- **Citizen data sent to third parties:** `When assessment is requested, the selected issue category and the resident's Before image plus worker's After image are sent to Google Gemini solely for visual assessment.`
- **Cost at city scale:** `Not measured yet; production rollout would require quota monitoring, retry limits, and a budget for visual-model requests.`

## 4. Key Prompts (optional, max 5)

<!-- Only prompts that shaped a real design or code decision. Not a full chat log. -->

| # | Prompt (short) | What we kept | What we changed or rejected |
|---|---|---|---|
| 1 | `Design a role-based civic complaint workflow with public, worker, and MCC views.` | `Separate dashboards and clear role-specific actions.` | `We kept our own workflow rules and assignment behavior.` |
| 2 | `Suggest an approach for comparing Before and After civic-issue photos.` | `Gemini visual assessment with a score and explanation.` | `We rejected fabricated image metrics and require Gemini output for the final assessment.` |
| 3 | `Help diagnose deployment and browser CORS failures.` | `Configuration and debugging guidance.` | `The team tested fixes against the deployed frontend and backend.` |

## 5. How We Verified AI Output

- We tested public, worker, and MCC workflows with sample complaints before using them in the demo.
- We tested whether an uploaded Before and After image can be displayed to each permitted role and whether the Gemini result is visible after assessment.
- We caught and corrected deployment issues including missing backend dependencies and browser CORS configuration through local and deployed testing.
- We rejected any UI or documentation claim that did not match the implemented workflow.

## 6. What We Deliberately Did *Not* Use AI For

- The team made the final product, role, and worker-area allocation decisions.
- The team reviewed and tested the final code and deployment configuration.
- We did not train or fine-tune an image model; Gemini is used as a provider API at runtime.

---

**Declaration:** We confirm this disclosure is complete, and every team member can explain the code listed above.
**Signed:** `Bhavish S` on behalf of `Code Breakers (CB001)` · `20 September 2026`
