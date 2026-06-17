# Scenario Modeller Streamlit MVP

A lightweight prototype front-end for configuring and running portfolio planning scenarios.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Purpose

This app demonstrates a clean separation between:

- Streamlit user interface
- scenario configuration data
- Python scenario engine
- operation functions
- result visualisation and export

## MVP operations included

- NoChange
- Exclude
- Delay
- PriceAdj
- FarmDown_Proceeds
- FarmDown_Carry
- FarmDown_Hybrid

The included data is mock data only.
