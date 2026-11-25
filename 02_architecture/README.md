# Solution Architecture

The diagrams trace the modelling workflow from governed financial and production data through scenario configuration, calculation and analysis. Start with the overall diagram, then use diagrams 002–006 for data preparation and the Excel interface, or 007–009 for scenario configuration and engine execution.

## Diagram catalogue

1. [Overall Solution Architecture](svg/001_overall_solution_architecture.svg)
2. [Semantic Model Data Integration](svg/002_semantic_model_data_integration.svg)
3. [Controlled Transaction Scope](svg/003_controlled_transaction_scope.svg)
4. [Controlled Manual Profile Integration](svg/004_controlled_manual_profile_integration.svg)
5. [Financial Entity to Modelling Case Translation](svg/005_financial_entity_case_translation.svg)
6. [Semantic Model to Excel Interface](svg/006_semantic_model_to_excel_interface.svg)
7. [Scenario Configuration Workflow](svg/007_scenario_configuration_workflow.svg)
8. [Python Engine Architecture](svg/008_python_engine_architecture.svg)
9. [Python Engine Dependency Map](svg/009_python_engine_dependency_map.svg)

The [editable master draw.io diagram](source/000_master_architecture_diagram.drawio) contains the source for the SVG exports.

### Viewing the SVG diagrams

Individual architecture diagrams are provided as SVG files to preserve image quality and scalability.

GitHub's standard file preview may not render some SVG files correctly. If this occurs, the diagrams can be viewed by:

- opening the repository in **VS Code**;
- opening the repository in **GitHub Codespaces**; or
- opening the SVG file locally in a compatible browser or image viewer.

## Implementation

- [Semantic Model](../00_semantic_model/README.md)
- [Excel Scenario Modelling Application](../01_excel_application/README.md)
- [Testing and Validation](../03_testing_and_validation/README.md)
