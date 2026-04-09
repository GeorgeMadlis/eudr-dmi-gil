# Inspection Index (Authoritative Implementation)

This document is the canonical implementation-grounding index for the
EUDR DAO Digital Twin Engineer (DTE) and for developers working from DAO
inspection findings.

Use this file to answer two questions:

1. Which repository is authoritative for this question?
2. Which document should I open next for grounded evidence?

## Authority boundary

- `eudr-dmi-gil` is authoritative for:
  - evidence contracts and bundle layout
  - deterministic report generation
  - dependency provenance and source registries
  - implementation architecture, tests, and regeneration workflows
- `eudr-dmi-gil-digital-twin` is the public, non-authoritative inspection
  and governance surface.
- `eudr-client-portal` is authoritative for portal UX, chat routing,
  privacy boundaries, bundle ingestion, and user-facing report flows.
  It is not authoritative for geospatial analytics or compliance logic.

When a question mixes repos, keep authority separated in the answer.
Do not present portal or Digital Twin summaries as authoritative
implementation facts.

## DTE grounding rule

Implementation recommendations must cite one or more paths from this file.
If you cannot ground an implementation claim to a path below, mark it as an
**Evidence gap**.

For public inspection findings, first open the relevant Digital Twin artefact,
then use this index to map the finding back to implementation documents.

## How to use this index

1. Identify the question type.
2. Open the authoritative section below.
3. If the question is about public inspection, also open the corresponding
   Digital Twin document.
4. If the question is about portal behavior, privacy, or chat surfaces, also
   open the corresponding portal document.
5. If documents disagree, prefer authority in this order:
   - `eudr-dmi-gil` for implementation, artefact contracts, and generation
   - `eudr-dmi-gil-digital-twin` for published inspection URLs and DAO framing
   - `eudr-client-portal` for portal behavior and chat/product surfaces

## Question-to-doc routing

### AOI report structure, artefacts, and publication contract

Open these first:

- `docs/reports/README.md`
- `docs/reports/runbook_generate_aoi_report.md`
- `docs/architecture/decision_records/0001-report-pipeline-architecture.md`

Open in the Digital Twin repo for the public inspection view:

- `eudr-dmi-gil-digital-twin/docs/dte_instructions.md`
- `eudr-dmi-gil-digital-twin/docs/DT_LINK_REGISTRY.md`
- `eudr-dmi-gil-digital-twin/docs/implementation_mirror/report_outputs.md`

Use for questions like:

- What artefacts must a published AOI run contain?
- What does `report.html` need to link to?
- Which files are source-of-truth for AOI inspection?
- Which public runs are currently intended for inspection?

### Evidence sufficiency, policy mapping, and DAO acceptance criteria

Open these first:

- `docs/reports/README.md`
- `docs/governance/roles_and_workflow.md`
- `docs/architecture/decision_records/0001-report-pipeline-architecture.md`

Open in the Digital Twin repo:

- `eudr-dmi-gil-digital-twin/docs/regulation/policy_to_evidence_spine.md`
- `eudr-dmi-gil-digital-twin/docs/dao/proposal_schema.md`
- `eudr-dmi-gil-digital-twin/docs/agent_prompts/dao_stakeholders_prompt.md`
- `eudr-dmi-gil-digital-twin/docs/agent_prompts/dao_dev_prompt.md`

Use for questions like:

- Which artefact supports Article 9, 10, or 11 inspection?
- What counts as enough evidence for a DAO proposal?
- How should a Session Closeout or proposal be structured?

### Dependencies, provenance, and upstream evidence sources

Open these first:

- `docs/dependencies/README.md`
- `docs/dependencies/sources.md`
- `docs/dependencies/flow.md`
- `docs/architecture/dependency_register.md`

Open in the Digital Twin repo:

- `eudr-dmi-gil-digital-twin/docs/regulation/sources.md`
- `eudr-dmi-gil-digital-twin/docs/implementation_mirror/dependency_model.md`

Use for questions like:

- Which upstream sources are tracked?
- Where should provenance or audit files live?
- Which code paths are publicly preserved as stable references?
- How do dependency changes trigger regeneration or DAO proposals?

### Determinism, regeneration, and publish workflow

Open these first:

- `docs/architecture/decision_records/0001-report-pipeline-architecture.md`
- `docs/reports/runbook_generate_aoi_report.md`
- `docs/operations/environment_setup.md`
- `docs/operations/minio_setup.md`
- `docs/operations/migration_runbook.md`

Helpful supporting docs:

- `README.md`
- `CHANGELOG.md`
- `data/README.md`
- `data_db/README.md`

Use for questions like:

- How are bundles regenerated deterministically?
- Which commands are the required smoke/regression path?
- Where are outputs written before Digital Twin publish?
- Which changes require reruns or republishing?

### Public inspection navigation and governance framing

The authoritative implementation lives here, but public inspection navigation
is documented in the Digital Twin repo. Open:

- `eudr-dmi-gil-digital-twin/README.md`
- `eudr-dmi-gil-digital-twin/docs/dte_instructions.md`
- `eudr-dmi-gil-digital-twin/docs/DT_LINK_REGISTRY.md`
- `eudr-dmi-gil-digital-twin/docs/views/digital_twin_view.md`
- `eudr-dmi-gil-digital-twin/docs/views/task_view.md`
- `eudr-dmi-gil-digital-twin/docs/views/agentic_view.md`

Use for questions like:

- Which public URLs may DTE inspect?
- What is the correct portal navigation path for AOI runs?
- Which repo owns which step in the DAO loop?

### Portal behavior, chat surfaces, and private/public boundaries

These questions are not implementation-authoritative unless they point back
to `eudr-dmi-gil`, but they are authoritative for portal behavior.
Open in `eudr-client-portal`:

- `eudr-client-portal/docs/skills/Files to Upload to EUDR Client Portal in Claude.md`
- `eudr-client-portal/README.md`
- `eudr-client-portal/docs/skills/01_portal_claude_project.md`
- `eudr-client-portal/docs/architecture/public_private_knowledge_strategy.md`
- `eudr-client-portal/docs/architecture/llm_topology.md`
- `eudr-client-portal/docs/eudr_report_current_state.md`
- `eudr-client-portal/docs/ui/aoi_run_workflow.md`
- `eudr-client-portal/docs/skills/02_public_inspector_chat.md`
- `eudr-client-portal/docs/skills/03_private_inspector_chat.md`

Use for questions like:

- Which portal docs are the primary synthesized knowledge packs?
- How does the portal invoke `eudr-dmi-gil`?
- Which chat surfaces are public vs private?
- How are run artefacts ingested, stored, and exposed?
- What does the user see on the run page?

### Question-specific EUDR and report-answering references

These are supplementary question-routing docs in `eudr-client-portal`.
They are useful for DTE setup and inspector-chat answer quality, but they do
not replace authoritative implementation or opened Digital Twin artefacts.

Reading order inside `eudr-client-portal`:

1. `docs/skills/Files to Upload to EUDR Client Portal in Claude.md`
2. `docs/skills/02_public_inspector_chat.md` or
   `docs/skills/03_private_inspector_chat.md`
3. the narrower `docs/skills/chat-skills/...` references below

The `docs/skills/02_*` and `03_*` files are the primary synthesized knowledge
packs. The `chat-skills` files add narrower reasoning patterns for specific
question types.

Public guidance:

- `eudr-client-portal/docs/eudr/summary.md`
- `eudr-client-portal/docs/skills/chat-skills/public/04_commodity_operator_applicability.md`
- `eudr-client-portal/docs/skills/chat-skills/public/05_country_risk_dds_workflow.md`
- `eudr-client-portal/docs/skills/chat-skills/public/06_reading_demo_reports.md`

Private run interpretation:

- `eudr-client-portal/docs/skills/chat-skills/private/07_bundle_manifest_cross_reference.md`
- `eudr-client-portal/docs/skills/chat-skills/private/08_fail_triage.md`
- `eudr-client-portal/docs/skills/chat-skills/private/09_metrics_interpretation.md`

Use for questions like:

- Does EUDR apply to this operator or commodity?
- What does a PASS, FAIL, or N/A report mean?
- How should a manifest or metric be explained to a user?
- How should a FAIL verdict be triaged?

### DTE setup and upload-pack guidance

If the question is about how to configure AI context for this project, start in
`eudr-client-portal`:

- `eudr-client-portal/docs/skills/Files to Upload to EUDR Client Portal in Claude.md`
- `eudr-client-portal/docs/skills/01_portal_claude_project.md`
- `eudr-client-portal/docs/skills/02_public_inspector_chat.md`
- `eudr-client-portal/docs/skills/03_private_inspector_chat.md`

Use for questions like:

- Which docs are the minimum viable upload set?
- Which docs are primary syntheses vs supplementary originals?
- Which knowledge pack should be used for developer, public inspector, or
  private inspector contexts?

## Core authoritative documents in this repo

### Architecture

- `README.md`
- `docs/architecture/decision_records/0001-report-pipeline-architecture.md`
- `docs/architecture/dependency_register.md`

### Reports and output contracts

- `docs/reports/README.md`
- `docs/reports/runbook_generate_aoi_report.md`

### Dependencies and provenance

- `docs/dependencies/README.md`
- `docs/dependencies/sources.md`
- `docs/dependencies/flow.md`

### Governance and workflow

- `docs/governance/roles_and_workflow.md`
- `ADOPTION_LOG.md`

### Operations

- `docs/operations/environment_setup.md`
- `docs/operations/minio_setup.md`
- `docs/operations/migration_runbook.md`

### Supporting repository context

- `data/README.md`
- `data_db/README.md`
- `aoi_json_examples/README.md`
- `tests/fixtures/hansen/README.md`
- `DEV_NOTES.md`
- `scripts/migrate_from_private_eudr_dmi/README.md`

## Cross-repo quick map

| Need | Authoritative first stop | Supporting inspection docs |
|---|---|---|
| AOI artefact contract | `docs/reports/README.md` | `eudr-dmi-gil-digital-twin/docs/dte_instructions.md` |
| Deterministic generation | `docs/reports/runbook_generate_aoi_report.md` | `eudr-dmi-gil-digital-twin/docs/implementation_mirror/report_pipeline.md` |
| Dependency provenance | `docs/dependencies/sources.md` | `eudr-dmi-gil-digital-twin/docs/regulation/sources.md` |
| DAO proposal grounding | `docs/governance/roles_and_workflow.md` | `eudr-dmi-gil-digital-twin/docs/dao/proposal_schema.md` |
| Public inspection URLs | `eudr-dmi-gil-digital-twin/docs/DT_LINK_REGISTRY.md` | `eudr-dmi-gil-digital-twin/README.md` |
| Portal UX or chat behavior | `eudr-client-portal/docs/eudr_report_current_state.md` | `eudr-client-portal/docs/skills/02_public_inspector_chat.md` |

## Practical DTE notes

- Treat `eudr-client-portal` skill documents as answer-shaping guidance, not
  as substitutes for opened DT artefacts or authoritative implementation docs.
- When public URLs, run names, or AOI navigation rules matter, prefer the
  Digital Twin docs over older portal summaries.
- When artefact names or bundle layout matter, prefer `docs/reports/*` in this
  repo over mirrored summaries elsewhere.
- If a supporting doc appears stale or conflicts with current public artefacts,
  record an **Evidence gap** or propose a doc-alignment change rather than
  silently reconciling it.
