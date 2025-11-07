# Port Risk Assessment Analysis Tool

This project provides a comprehensive analysis and visualization tool for port risk assessment data collected from Brazilian port organizations.

## Project Overview

The tool analyzes risk assessment data covering:
- **Economic Risks** (21 categories): Market speculation, debt issues, supply chain disruptions
- **Environmental Risks** (18 categories): Climate change, biodiversity loss, pollution
- **Geopolitical Risks** (8 categories): Conflicts, sanctions, terrorism, migration
- **Social Risks** (16 categories): Human rights, public services, workplace safety
- **Technological Risks** (17 categories): AI consequences, cybersecurity, automation

## Features

### Data Analysis
- Risk scoring and aggregation across different dimensions
- Comparative analysis between port types (Public, Private, Operators, Regulators)
- Geographic risk mapping by Brazilian states
- Time-based risk trend analysis (2025, 2026-2027, up to 2035)

### Visualization
- Interactive risk heat maps
- Risk radar charts for different organization types
- Geographic risk distribution maps
- Trend analysis charts
- Risk comparison dashboards

### Reporting
- Executive summaries for stakeholders
- Detailed risk assessment reports
- Comparative analysis between ports/regions
- Export capabilities for presentations

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation (Recommended - Virtual Environment)

1. Clone or download this project
2. Run the automated setup script:
```bash
.\setup_venv.bat
```

This will:
- Create a virtual environment named `venv`
- Activate the environment
- Install all required dependencies
- Run a data preview to verify setup

### Manual Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the analysis tool:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:8050`

### Quick Data Preview
To see your data structure and preview:
```bash
python show_data_head.py
```

## Usage

1. **Data Loading**: The tool automatically loads the `questionario.xlsx` file
2. **Dashboard Navigation**: Use the sidebar to navigate between different analysis views
3. **Filtering**: Apply filters by port type, state, or risk category
4. **Export**: Download reports and visualizations using the export buttons

## File Structure

```
riscos_portuarios/
├── app.py                 # Main application file
├── data_processor.py      # Data processing and analysis
├── requirements.txt       # Python dependencies
├── questionario.xlsx      # Raw risk assessment data
├── outputs/              # Generated reports and visualizations
└── README.md             # This file
```

## Data Source

The analysis is based on responses from:
- **Respondents**: 80+ port organizations across Brazil
- **Time Period**: September-October 2025
- **Risk Scoring**: 1-5 scale for likelihood and impact assessment
- **Coverage**: 15+ Brazilian states and various port organization types

## Technical Details

- **Backend**: Python with pandas, numpy, plotly
- **Frontend**: Dash web framework for interactive visualizations
- **Data Processing**: Automated cleaning and structuring of Excel data
- **Visualization**: Interactive charts and maps using Plotly

## Support

For questions or issues with the tool, please refer to the code comments or contact the development team.
