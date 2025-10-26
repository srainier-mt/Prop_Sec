# Propulsion Performance Analyzer

This project provides a lightweight browser-based tool for exploring APC
propeller performance files together with brushless motor specifications. The
included Streamlit application parses APC `.dat` or PDF reports, computes the
motor current/voltage required to deliver each tabulated thrust value, and plots
key propulsion metrics.

## Quick start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Launch the Streamlit application:

   ```bash
   streamlit run app.py
   ```

3. Open the provided URL in your browser. Upload an APC `.dat` file (or use the
   bundled `APC 17x8.pdf` sample) and enter your motor's Kv, resistance, supply
   voltage, and current limits to view performance plots.

## Testing

Run the automated smoke tests to verify that the bundled APC dataset parses
correctly and that the motor performance pipeline generates the expected
columns:

```bash
pytest
```

The suite loads `APC 17x8.pdf`, computes a representative motor setup, and
asserts that feasible operating points and finite efficiency values are
produced.

## Features

- Automatic parsing of APC propeller datasets exported either as plain text or
  PDF reports.
- Derived motor performance metrics based on user-supplied electrical
  parameters (Kv, winding resistance, supply voltage, and current limits).
- Interactive tables and plots showing thrust, current draw, and efficiency
  versus airspeed for each available RPM block.

## File structure

- `app.py`: Streamlit application entry point.
- `prop_tool/parser.py`: Parser for APC `.dat` or PDF data files.
- `prop_tool/analysis.py`: Motor performance calculations.
- `APC 17x8.pdf`: Sample data set bundled for quick experimentation.

Feel free to extend the tool with additional visualisations or to import
multiple motor/propeller combinations for comparison.
