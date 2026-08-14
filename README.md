# Upstream Portfolio Scenario Modelling Framework

## Project Overview

This repository contains the technical artefacts developed for an Upstream portfolio scenario modelling framework designed to support long-term planning and portfolio analysis.

The project addresses a business need for a more **controlled, transparent and reproducible approach to scenario modelling**, reducing reliance on repeated manual spreadsheet manipulation while retaining the flexibility required by expert portfolio and finance users.

The framework enables users to construct alternative portfolio scenarios by selecting modelling cases and applying controlled operations such as timing changes, participation changes, truncation and financial or production adjustments. These decisions are translated into standardised instructions and executed through a modular Python scenario engine.

The solution is designed as **decision support rather than automated decision-making**. Users retain responsibility for scenario assumptions, configuration, interpretation and subsequent business decisions.

## Solution Architecture

The implemented framework combines:

* a governed semantic model providing standardised financial, production and reference data;
* controlled integration of approved manual modelling profiles;
* Financial Entity to Modelling Case translation;
* purpose-specific interfaces between the semantic model and Excel;
* guided scenario configuration and embedded validation;
* a modular Python-in-Excel scenario modelling engine;
* pre-tax, post-tax and discounted cash-flow calculations;
* Power Pivot and DAX for interactive aggregation and scenario analysis; and
* validation, logging and traceability throughout the modelling workflow.

The architecture applies principles including **data minimisation, purpose limitation, transparency, traceability, human oversight, consistent treatment, separation of concerns and governance by design**.

## Repository Navigation

    Upstream-Portfolio-Scenario-Modelling/
    │
    ├── 00_semantic_model/
    │   └── Documentation and sanitised artefacts describing the
    │       governed semantic layer supporting the modeller
    │
    ├── 01_excel_application/
    │   ├── Upstream_Portfolio_Scenario_Modeller_Sanitised.xlsm
    │   ├── DAX/
    │   │   ├── oledb_queries/
    │   │   └── power_pivot_measures/
    │   ├── power_query/
    │   ├── python/
    │   └── vba/
    │
    ├── 02_architecture/
    │   ├── source/
    │   │   └── Master editable draw.io architecture file
    │   └── svg/
    │       └── Published architecture and engineering diagrams
    │
    ├── 03_evidence/
    │   └── Selected sanitised testing and validation evidence
    │
    └── README.md

### `00_semantic_model`

Documents the governed semantic layer that provides the principal source dataset for the modelling framework, including data integration, transaction scoping, calculated members and supporting reference structures.

### `01_excel_application`

Contains the **sanitised Excel scenario modelling application** together with the extracted implementation artefacts supporting its operation:

* **Excel application** — sanitised version of the implemented scenario modeller;
* **DAX** — semantic-model queries and Power Pivot analytical measures;
* **Power Query** — data preparation and integration logic;
* **Python** — scenario engine, operation library, tax and discounted cash-flow processing;
* **VBA** — application navigation, execution and refresh controls.

### `02_architecture`

Contains the technical architecture and engineering diagrams developed for the Upstream Portfolio Scenario Modelling Framework.

The architecture folder is divided into:

* **`source/`** — the master editable draw.io file used to maintain the architecture diagrams;
* **`svg/`** — individual SVG exports for viewing and use within project documentation.

#### Viewing the Architecture Diagrams

Individual architecture diagrams are provided as SVG files to preserve image quality and scalability.

GitHub's standard file preview may not render some SVG files correctly. If this occurs, the diagrams can be viewed by:

* opening the repository in **VS Code**;
* opening the repository in **GitHub Codespaces**; or
* downloading and opening the SVG file locally in a compatible browser or image viewer.

The editable master source is retained separately in the `source/` folder.

#### Architecture Diagram Set

The diagram set documents the framework from end-to-end solution architecture through to detailed technical implementation:

1. **Overall Solution Architecture**
2. **Semantic Model Data Preparation and Integration**
3. **Controlled Transaction Scope and Calculated Member Derivation**
4. **Controlled Manual Profile Integration**
5. **Financial Entity to Modelling Case Translation**
6. **Controlled Semantic Model to Excel Interface**
7. **Scenario Configuration, Decision Workflow and Model Instruction Generation**
8. **Python Scenario Modelling Engine Architecture**
9. **Python Scenario Modelling Engine and Dependency Map**

Together, these diagrams describe the flow from governed source data through data preparation, scenario configuration and model execution to analytical outputs.

### `03_evidence`

Contains selected sanitised evidence supporting technical testing, performance assessment and business validation.

Full business evidence and confidential project materials are maintained separately within controlled enterprise locations and are not reproduced in this repository.

## Design and Governance Principles

The framework has been developed around several core principles:

* **Transparency:** assumptions, transformations and modelling logic should remain inspectable.
* **Traceability:** source data, case mappings, scenario operations and parameters should remain identifiable throughout the modelling workflow.
* **Human oversight:** the framework supports expert judgement rather than replacing accountable business decision-making.
* **Consistency:** common modelling operations are applied systematically across comparable cases and scenarios.
* **Data minimisation:** only data required for the modelling purpose is selected and processed.
* **Purpose limitation:** data extraction and transformation are designed specifically around the scenario-modelling requirement.
* **Separation of concerns:** data preparation, scenario configuration, calculation and analytical consumption remain logically distinct.
* **Governance by design:** controlled inputs, validation and standardised structures are embedded throughout the framework.

## Technology

The implemented solution uses a combination of:

**Power BI semantic modelling | DAX | OLE DB | Excel | Power Query | Python in Excel | pandas | VBA | Power Pivot | Git/GitHub**

The architecture deliberately separates the underlying modelling logic from presentation wherever practical, supporting future evolution of individual technology components without requiring the scenario methodology itself to be redesigned.

## Security and Confidentiality

This repository contains **code, architecture and sanitised technical documentation only**.

It must not contain:

* confidential planning or portfolio data;
* commercially sensitive case values;
* credentials, access tokens or connection secrets;
* unrestricted copies of confidential source datasets.

Enterprise data remains subject to the organisation's established access controls, information classification and governance requirements.

## Project Context

The framework was developed as part of a Digital & Technology Solutions Professional degree project and in response to a real Upstream portfolio-planning requirement.

The accompanying research examined how a governed scenario modelling framework could improve **transparency, reproducibility and trusted decision support** within an expert analytical environment. The implementation provides a practical proof of concept through which those principles can be technically and operationally evaluated.

## Recommended VS Code Extensions

The repository contains Python, DAX, Power Query/M, draw.io, Markdown and PDF artefacts.

A set of recommended VS Code extensions is provided in `.vscode/extensions.json` to improve syntax highlighting and file preview support.

These extensions are **developer conveniences only** and are not runtime dependencies of the modelling solution.

---