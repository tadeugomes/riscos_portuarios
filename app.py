"""
Port Risk Assessment Dashboard

Main application file for the interactive web-based risk analysis dashboard.
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_processor import PortRiskDataProcessor
import os

# Initialize the data processor
processor = PortRiskDataProcessor()

# Load and process data
try:
    processor.load_data()
    metadata = processor.extract_metadata()
    processed_data = processor.process_risk_data()
    statistics = processor.calculate_risk_statistics()
    risk_matrices = processor.get_risk_matrix_data()
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")
    # Create empty dataframes for graceful handling
    processed_data = pd.DataFrame()
    statistics = {}
    risk_matrices = {}

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Port Risk Assessment Dashboard"

# Define the layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Port Risk Assessment Dashboard", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # Navigation and Filters
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filters", className="card-title"),
                    html.Label("Port Type:"),
                    dcc.Dropdown(
                        id='port-type-filter',
                        options=[
                            {'label': 'All', 'value': 'all'}
                        ] + [{'label': pt, 'value': pt} for pt in processed_data['port_type'].unique() if pd.notna(pt)],
                        value='all',
                        className="mb-3"
                    ),
                    html.Label("State:"),
                    dcc.Dropdown(
                        id='state-filter',
                        options=[
                            {'label': 'All', 'value': 'all'}
                        ] + [{'label': state, 'value': state} for state in processed_data['state'].unique() if pd.notna(state)],
                        value='all',
                        className="mb-3"
                    ),
                    html.Label("Risk Category:"),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[
                            {'label': 'All', 'value': 'all'}
                        ] + [{'label': cat, 'value': cat} for cat in processed_data['risk_category'].unique()],
                        value='all',
                        className="mb-3"
                    ),
                    html.Label("Time Period:"),
                    dcc.Dropdown(
                        id='period-filter',
                        options=[
                            {'label': 'All', 'value': 'all'}
                        ] + [{'label': period, 'value': period} for period in processed_data['time_period'].unique()],
                        value='all',
                        className="mb-3"
                    )
                ])
            ])
        ], width=3),
        
        dbc.Col([
            # Key Metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Total Responses", className="card-subtitle"),
                            html.H4(f"{metadata.get('total_responses', 0)}", className="text-primary")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Risk Categories", className="card-subtitle"),
                            html.H4(f"{len(processed_data['risk_category'].unique()) if not processed_data.empty else 0}", className="text-info")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("States Covered", className="card-subtitle"),
                            html.H4(f"{len(processed_data['state'].unique()) if not processed_data.empty else 0}", className="text-success")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Port Types", className="card-subtitle"),
                            html.H4(f"{len(processed_data['port_type'].unique()) if not processed_data.empty else 0}", className="text-warning")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # Main Content Area
            dcc.Tabs(id='main-tabs', value='overview', children=[
                dcc.Tab(label='Overview', value='overview'),
                dcc.Tab(label='Risk Analysis', value='risk-analysis'),
                dcc.Tab(label='Comparative Analysis', value='comparative'),
                dcc.Tab(label='Geographic View', value='geographic'),
                dcc.Tab(label='Top Risks', value='top-risks'),
                dcc.Tab(label='Data Export', value='export')
            ]),
            
            html.Div(id='tab-content', className="mt-4")
        ], width=9)
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Port Risk Assessment Dashboard - Generated from questionnaire data", className="text-center text-muted")
        ])
    ])
], fluid=True)

# Callback for tab content
@callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value'),
    Input('port-type-filter', 'value'),
    Input('state-filter', 'value'),
    Input('category-filter', 'value'),
    Input('period-filter', 'value')
)
def render_tab_content(active_tab, port_type, state, category, period):
    if processed_data.empty:
        return html.Div("No data available. Please check your data source.")
    
    # Filter data based on selections
    filtered_data = processed_data.copy()
    
    if port_type != 'all':
        filtered_data = filtered_data[filtered_data['port_type'] == port_type]
    if state != 'all':
        filtered_data = filtered_data[filtered_data['state'] == state]
    if category != 'all':
        filtered_data = filtered_data[filtered_data['risk_category'] == category]
    if period != 'all':
        filtered_data = filtered_data[filtered_data['time_period'] == period]
    
    # Filter only numeric scores for calculations
    numeric_data = filtered_data[
        filtered_data['risk_score'].apply(lambda x: isinstance(x, (int, float)))
    ]
    
    if active_tab == 'overview':
        return render_overview_tab(numeric_data)
    elif active_tab == 'risk-analysis':
        return render_risk_analysis_tab(numeric_data)
    elif active_tab == 'comparative':
        return render_comparative_tab(numeric_data)
    elif active_tab == 'geographic':
        return render_geographic_tab(numeric_data)
    elif active_tab == 'top-risks':
        return render_top_risks_tab(numeric_data)
    elif active_tab == 'export':
        return render_export_tab(filtered_data)

def render_overview_tab(data):
    """Render overview tab with summary visualizations"""
    
    # Risk levels by category
    if not data.empty:
        category_risks = data.groupby('risk_category')['risk_score'].mean().reset_index()
        
        fig_category = px.bar(
            category_risks,
            x='risk_category',
            y='risk_score',
            title="Average Risk Score by Category",
            labels={'risk_score': 'Average Risk Score', 'risk_category': 'Risk Category'}
        )
        fig_category.update_layout(showlegend=False)
        
        # Risk by time period
        period_risks = data.groupby('time_period')['risk_score'].mean().reset_index()
        
        fig_period = px.line(
            period_risks,
            x='time_period',
            y='risk_score',
            title="Risk Trends Over Time",
            labels={'risk_score': 'Average Risk Score', 'time_period': 'Time Period'},
            markers=True
        )
        
        # Risk distribution
        fig_dist = px.histogram(
            data,
            x='risk_score',
            title="Distribution of Risk Scores",
            labels={'risk_score': 'Risk Score', 'count': 'Frequency'},
            nbins=20
        )
    else:
        fig_category = go.Figure()
        fig_period = go.Figure()
        fig_dist = go.Figure()
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_category)
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_period)
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_dist)
                ])
            ])
        ], width=12, className="mt-3")
    ])

def render_risk_analysis_tab(data):
    """Render risk analysis tab with detailed visualizations"""
    
    if not data.empty:
        # Heatmap of risks by category and time period
        heatmap_data = data.pivot_table(
            values='risk_score',
            index='risk_category',
            columns='time_period',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Risk Heatmap by Category and Time Period",
            labels=dict(x="Time Period", y="Risk Category", color="Risk Score")
        )
        
        # Box plot by category
        fig_box = px.box(
            data,
            x='risk_category',
            y='risk_score',
            title="Risk Score Distribution by Category",
            labels={'risk_score': 'Risk Score', 'risk_category': 'Risk Category'}
        )
    else:
        fig_heatmap = go.Figure()
        fig_box = go.Figure()
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_heatmap)
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_box)
                ])
            ])
        ], width=6)
    ])

def render_comparative_tab(data):
    """Render comparative analysis tab"""
    
    if not data.empty:
        # Compare by port type
        port_comparison = data.groupby(['port_type', 'risk_category'])['risk_score'].mean().reset_index()
        
        fig_port = px.bar(
            port_comparison,
            x='port_type',
            y='risk_score',
            color='risk_category',
            title="Risk Comparison by Port Type",
            labels={'risk_score': 'Average Risk Score', 'port_type': 'Port Type'},
            barmode='group'
        )
        
        # Compare by state (top 10 states)
        state_comparison = data.groupby('state')['risk_score'].mean().sort_values(ascending=False).head(10).reset_index()
        
        fig_state = px.bar(
            state_comparison,
            x='state',
            y='risk_score',
            title="Top 10 States by Average Risk Score",
            labels={'risk_score': 'Average Risk Score', 'state': 'State'}
        )
    else:
        fig_port = go.Figure()
        fig_state = go.Figure()
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_port)
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_state)
                ])
            ])
        ], width=6)
    ])

def render_geographic_tab(data):
    """Render geographic analysis tab"""
    
    if not data.empty:
        # State-wise risk analysis
        state_risks = data.groupby('state')['risk_score'].mean().reset_index()
        state_risks = state_risks.sort_values('risk_score', ascending=False)
        
        fig_state = px.bar(
            state_risks,
            x='risk_score',
            y='state',
            orientation='h',
            title="Risk Scores by State",
            labels={'risk_score': 'Average Risk Score', 'state': 'State'}
        )
        fig_state.update_layout(height=600)
        
        # Category distribution by state
        state_category = data.groupby(['state', 'risk_category'])['risk_score'].mean().reset_index()
        
        fig_state_cat = px.sunburst(
            state_category,
            path=['state', 'risk_category'],
            values='risk_score',
            title="Risk Distribution by State and Category"
        )
    else:
        fig_state = go.Figure()
        fig_state_cat = go.Figure()
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_state)
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_state_cat)
                ])
            ])
        ], width=4)
    ])

def render_top_risks_tab(data):
    """Render top risks tab"""
    
    if not data.empty:
        # Top 20 risks overall
        top_risks = data.groupby('risk_description')['risk_score'].mean().sort_values(ascending=False).head(20).reset_index()
        
        fig_top = px.bar(
            top_risks,
            x='risk_score',
            y='risk_description',
            orientation='h',
            title="Top 20 Highest Risk Items",
            labels={'risk_score': 'Average Risk Score', 'risk_description': 'Risk Description'}
        )
        fig_top.update_layout(height=600)
        
        # Top risks by category
        top_by_category = data.groupby(['risk_category', 'risk_description'])['risk_score'].mean().reset_index()
        top_by_category = top_by_category.sort_values(['risk_category', 'risk_score'], ascending=[True, False])
        
        fig_category = px.bar(
            top_by_category.head(30),
            x='risk_score',
            y='risk_description',
            color='risk_category',
            orientation='h',
            title="Top Risks by Category",
            labels={'risk_score': 'Average Risk Score', 'risk_description': 'Risk Description'}
        )
        fig_category.update_layout(height=600)
    else:
        fig_top = go.Figure()
        fig_category = go.Figure()
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_top)
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_category)
                ])
            ])
        ], width=6)
    ])

def render_export_tab(data):
    """Render export tab with data table and export options"""
    
    # Create data table
    if not data.empty:
        # Sample first 1000 rows for display
        display_data = data.head(1000)
        
        table = dash_table.DataTable(
            data=display_data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in display_data.columns],
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
        
        export_buttons = dbc.Row([
            dbc.Col([
                html.H5("Export Options"),
                html.P("Download the processed data in various formats:"),
                html.Ul([
                    html.Li("CSV format for spreadsheet analysis"),
                    html.Li("JSON format for programmatic use"),
                    html.Li("Excel format with all original data")
                ]),
                html.Hr(),
                dbc.Button("Download CSV", color="primary", className="me-2", href="/download/csv"),
                dbc.Button("Download JSON", color="success", className="me-2", href="/download/json"),
                dbc.Button("Download Excel", color="info", href="/download/excel")
            ])
        ])
    else:
        table = html.P("No data available for export.")
        export_buttons = html.P("No data available for export.")
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Data Preview", className="card-title"),
                    table
                ])
            ])
        ], width=8),
        dbc.Col([
            export_buttons
        ], width=4)
    ])

# Add download endpoints
@app.server.route('/download/csv')
def download_csv():
    """Download processed data as CSV"""
    if not processed_data.empty:
        output_path = 'outputs/processed_data.csv'
        processor.export_processed_data(output_path)
        return send_file(output_path, as_attachment=True)
    return "No data available"

@app.server.route('/download/json')
def download_json():
    """Download processed data as JSON"""
    if not processed_data.empty:
        import os
        os.makedirs('outputs', exist_ok=True)
        json_path = 'outputs/processed_data.json'
        processed_data.to_json(json_path, orient='records', indent=2)
        return send_file(json_path, as_attachment=True)
    return "No data available"

@app.server.route('/download/excel')
def download_excel():
    """Download original Excel file"""
    if os.path.exists('questionario.xlsx'):
        return send_file('questionario.xlsx', as_attachment=True)
    return "Original file not found"

# Add send_file import
from flask import send_file

if __name__ == '__main__':
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=8050)
