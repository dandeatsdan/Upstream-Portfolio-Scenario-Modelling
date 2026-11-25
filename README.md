# Upstream Portfolio Scenario Modelling Framework

## Project Overview

This repository contains the **working solution, source code, technical architecture, sanitised representative datasets, validation evidence, and user documentation** for an Upstream portfolio scenario modelling framework supporting long-term planning and portfolio analysis.

The project addresses a business need for a more **controlled, transparent, and reproducible approach to scenario modelling**, reducing reliance on repeated manual spreadsheet reconstruction while retaining the flexibility required by expert portfolio and finance users.

The implemented solution enables users to construct alternative portfolio scenarios by selecting modelling cases and applying controlled operations such as timing changes, participation changes, truncation, and financial or production adjustments. User selections are translated into standardised scenario instructions and executed through a modular Python-in-Excel modelling engine.

The framework combines a governed semantic data layer with a user-facing Excel application, allowing scenario assumptions to be applied consistently to financial and production profiles before outputs are aggregated and analysed interactively.

The solution is designed as **decision support rather than automated decision-making**. Users remain responsible for scenario assumptions, configuration, interpretation, and subsequent business decisions.

---

## Working Solution

The repository contains sanitised working versions of both principal solution components:

| Component | Working Artefact | Purpose |
| :-------- | :--------------- | :------ |
| Semantic Model | [Power BI Semantic Model](00_semantic_model/02_working_solution/data_pipeline.pbix) | Sanitised working semantic model providing the governed data-preparation layer and representative upstream datasets used by the modelling framework. |
| Excel Scenario Modeller | [Excel Scenario Modelling Application](01_excel_application/05_working_solution/scenario_modelling_application.xlsm) | Sanitised working Excel application containing the user interface, scenario configuration, Python modelling engine, validation controls, and analytical outputs. |

Production enterprise connections have been removed from these repository versions and replaced with representative sanitised datasets.

The objective of the repository artefacts is **functional and structural equivalence rather than numerical equivalence** with the production implementation.

The Excel application uses **worksheet protection** to preserve the intended interface and reduce the risk of accidental changes to formulas, shapes, controls, and other application components. Protection is intentionally applied **without a password**: it is a usability and model-integrity safeguard rather than a security control.

---

## Solution Architecture

The implemented framework combines:

- a governed semantic model providing standardised financial, production, and reference data;
- controlled integration of approved manual modelling profiles;
- Financial Entity to Modelling Case translation;
- purpose-specific interfaces between the semantic model and Excel;
- guided scenario configuration and embedded validation;
- a modular Python-in-Excel scenario modelling engine;
- timing, ownership, production, cost, and capital scenario operations;
- pre-tax, post-tax, and discounted cash-flow calculations;
- Power Pivot and DAX for interactive aggregation and scenario analysis;
- VBA controls for application navigation and execution;
- model-health logging and user-facing validation messages; and
- structured testing, business validation, and performance assessment.

The architecture applies principles including **data minimisation, purpose limitation, transparency, traceability, human oversight, consistent treatment, separation of concerns, and governance by design**.

---

## Repository Navigation

| Area | What to find |
| --- | --- |
| [Semantic Model](00_semantic_model/README.md) | Governed data preparation, Power Query modules and representative datasets. |
| [Excel Application](01_excel_application/README.md) | Scenario configuration, calculation engine, output capture and analysis. |
| [Solution Architecture](02_architecture/README.md) | Nine diagrams covering the end-to-end workflow, plus editable draw.io source. |
| [Testing and Validation](03_testing_and_validation/README.md) | Business validation, performance and scalability results, and SME walkthroughs. |
| [User Guides](04_user_guides/README.md) | Steps for configuring, validating, running and reviewing scenarios. |
| [Project Management](05_project_management/README.md) | Scope, delivery plan, governance, risks and success criteria. |
| [Development Journal](06_development_journal/README.md) | Project chronology, reflections and eleven supporting exhibits. |
| [Research and Requirements](07_research_and_requirements/README.md) | Research context, methods and prioritised stakeholder requirements. |

---

## Data and Repository Sanitisation

The production solution operates with governed enterprise data and controlled organisational infrastructure that cannot be reproduced within this repository.

Separate sanitised working versions of the semantic model and Excel application were therefore created for technical inspection and demonstration.

The sanitisation approach includes:

- substantial reduction of the source population;
- use of representative historic rather than current planning data;
- replacement of Financial Entity, geography, and organisational identifiers with synthetic labels and keys;
- displacement of historic periods to the demonstration modelling horizon;
- deterministic material rounding of financial and production values;
- removal of genuine forward-looking portfolio forecasts;
- use of dummy representative manual modelling profiles;
- removal of production server, database, SharePoint, and other infrastructure details; and
- retention only of the data required to demonstrate application structure and behaviour.

The resulting repository datasets are **representative demonstration data**. They preserve the schemas, relationships, transformation logic, and behaviour required to inspect the solution but must not be interpreted as genuine historical or forecast portfolio information.

---

## Design and Governance Principles

The framework has been developed around several core principles:

- **Transparency** — assumptions, transformations, operations, and model status should remain inspectable.
- **Traceability** — source structures, case mappings, scenario operations, parameters, and outputs should remain identifiable through the modelling workflow.
- **Human oversight** — users explicitly configure scenarios and retain responsibility for interpreting results and making subsequent decisions.
- **Consistency** — common modelling operations apply standardised logic across comparable cases and scenarios.
- **Data minimisation** — only information required for the modelling purpose is selected and processed.
- **Purpose limitation** — data extraction and transformation are specifically aligned to the defined scenario-modelling requirement.
- **Separation of concerns** — data preparation, business mapping, user configuration, calculation, and analytical consumption remain logically distinct.
- **Embedded validation** — preventative input controls and execution-stage validation reduce the risk of invalid scenario outputs.
- **Baseline preservation** — scenario operations transform copies of source profiles rather than modifying the governed baseline.
- **Governance by design** — controlled inputs, mappings, validation, model logging, and standardised structures are embedded throughout the framework.

---

## Technology

The implemented solution uses a combination of:

**Power BI semantic modelling | DAX | OLE DB | Excel | Power Query | Python in Excel | pandas | VBA | Power Pivot | Git/GitHub**

The architecture deliberately separates responsibilities across these technologies rather than embedding the full solution within a single application layer.

This enables the underlying scenario methodology, data preparation, user interface, calculation logic, and analytical presentation to evolve independently where appropriate.

---

## Security and Confidentiality

This repository contains **sanitised working artefacts, representative datasets, implementation code, technical architecture, user documentation, and selected validation evidence**.

It must not contain:

- confidential planning or portfolio data;
- genuine current or forward-looking portfolio forecasts;
- identifiable Financial Entity or organisational information;
- commercially sensitive detailed case outputs;
- credentials, access tokens, or connection secrets;
- production server, database, or SharePoint connection details; or
- unrestricted copies of controlled enterprise source datasets.

Production data and infrastructure remain subject to the organisation's established information-classification, access-control, and governance requirements.

Detailed confidential validation evidence and business materials are retained separately within controlled enterprise locations.

---

## Project Context

The framework was developed as part of a **Digital & Technology Solutions Professional degree project** and in response to a real Upstream portfolio-planning requirement.

The [Research and Requirements evidence pack](07_research_and_requirements/research_and_requirements.pdf) examined whether a governed scenario modelling framework could improve **transparency, reproducibility, and trusted decision support** within an expert analytical environment.

The implemented solution provides a practical demonstration of those principles through:

- governed data preparation;
- structured modelling-case definition;
- standardised scenario operations;
- automated financial transformation;
- embedded validation;
- transparent scenario comparison; and
- professional technical documentation and testing.

The repository provides the principal technical evidence base for understanding, inspecting, maintaining, and potentially extending the implemented framework.

---

## Recommended VS Code Extensions

The repository contains Python, DAX, Power Query/M, draw.io, Markdown, CSV, and PDF artefacts.

A set of recommended VS Code extensions is provided in [`.vscode/extensions.json`](.vscode/extensions.json) to improve syntax highlighting and file-preview support.

These extensions are **developer conveniences only** and are not runtime dependencies of the modelling solution.

---
