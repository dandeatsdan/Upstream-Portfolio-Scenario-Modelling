# Project Background

Purpose:

Create a governed scenario modelling framework for upstream portfolio planning.

Planning horizon:
2025-2040

Anchor year:
2024

Current implementation:
Python engine originally developed in Excel.

Core data structure:

Case
Metric
Year
Value

Operations currently supported:

- NoChange
- Delay
- Accelerate
- Dilution
- Increase
- TruncateBefore
- TruncateAfter
- PriceAdj_Simple
- FarmDown_Proceeds
- FarmDown_Carry
- FarmDown_Hybrid

Scenario Structure:

Scenario
    -> Cases
        -> Operations
            -> Parameters

Every operation should be auditable.

Every run should generate an audit trail.

Target users:

Portfolio planners
Commercial analysts
Finance analysts

Primary design goals:

1. Transparency
2. Reproducibility
3. Trust
4. Governance
5. Flexibility