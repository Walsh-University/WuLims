# Chain of Custody

This page documents the current chain-of-custody-related data in WuLims and the implementation status.

## Current Implementation Status

There is no standalone `chainofcustody` Django app in this repository today.

Chain-of-custody information currently lives on the `samples.Sample` model and related sample analysis tables:

- `Sample.filtration`
- `Sample.preservation`
- `Sample.received_at`
- `Sample.status`
- `Sample.approved_at`
- `Sample.approved_by`
- `SampleAnalysis` records tied to each sample

Source of truth:
- `samples/models.py`

## What Is Tracked Per Sample

The current workflow tracks custody-related state at the sample level:

1. Intake timestamp (`received_at`)
2. Handling metadata (`filtration`, `preservation`)
3. Workflow status transitions (`RECEIVED` → `IN_PROGRESS` → `IN_REVIEW` → `APPROVED`/`REJECTED`)
4. Approval metadata (`approved_by`, `approved_at`)
5. Requested analyses via `SampleAnalysis`

## What Is Not Yet Implemented

The following are not yet modeled as first-class entities in this repo:

- COC header records (job number, page tracking, billing contact)
- Explicit custody event handoff table (relinquished/received signatures and timestamps)
- Dedicated printable COC document model/PDF pipeline

## Suggested Next Iteration (Optional)

If needed, COC can be expanded by introducing a dedicated app and models such as:

- `ChainOfCustody` (header-level metadata)
- `CustodyEvent` (handoff log)
- `ChainOfCustodySample` or FK from `Sample` to `ChainOfCustody`

Until then, operational custody data should be considered sample-scoped and maintained in `samples/`.
