"""
Data Processor for Port Risk Assessment Analysis

This module handles data loading, cleaning, and processing of the port risk assessment questionnaire data.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortRiskDataProcessor:
    """
    Handles processing of port risk assessment data from Excel questionnaire.
    """
    
    def __init__(self, excel_file_path: str = 'questionario.xlsx'):
        """
        Initialize the data processor.
        
        Args:
            excel_file_path: Path to the Excel file containing questionnaire data
        """
        self.excel_file_path = excel_file_path
        self.raw_data = None
        self.processed_data = None
        self.risk_categories = {
            'Economic': list(range(1, 22)),  # 1.1 to 1.21
            'Environmental': list(range(22, 40)),  # 2.1 to 2.18
            'Geopolitical': list(range(40, 48)),  # 3.1 to 3.8
            'Social': list(range(48, 64)),  # 4.1 to 4.16
            'Technological': list(range(64, 81))  # 5.1 to 5.17
        }
        self.time_periods = {
            'Immediate': 'Imediato (2025)',
            'Short Term': 'Curto prazo (2026 a 2027)',
            'Long Term': 'Longo prazo (até 2035)'
        }
        
    def load_data(self) -> pd.DataFrame:
        """
        Load data from Excel file.
        
        Returns:
            Raw DataFrame from Excel file
        """
        try:
            logger.info(f"Loading data from {self.excel_file_path}")
            self.raw_data = pd.read_excel(self.excel_file_path)
            logger.info(f"Loaded {len(self.raw_data)} rows and {len(self.raw_data.columns)} columns")
            return self.raw_data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def clean_column_names(self) -> pd.DataFrame:
        """
        Clean and standardize column names.
        
        Returns:
            DataFrame with cleaned column names
        """
        if self.raw_data is None:
            self.load_data()
            
        # Create a copy to avoid modifying original data
        df = self.raw_data.copy()
        
        # Clean column names
        cleaned_columns = []
        for col in df.columns:
            # Remove special characters and extra spaces
            cleaned = re.sub(r'[^\w\s]', '', str(col))
            cleaned = re.sub(r'\s+', '_', cleaned.strip())
            cleaned_columns.append(cleaned)
        
        df.columns = cleaned_columns
        logger.info("Column names cleaned")
        return df
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the dataset.
        
        Returns:
            Dictionary containing dataset metadata
        """
        if self.raw_data is None:
            self.load_data()
            
        metadata = {
            'total_responses': len(self.raw_data),
            'date_range': {
                'start': self.raw_data['Carimbo de data_hora'].min(),
                'end': self.raw_data['Carimbo de data_hora'].max()
            },
            'port_types': self.raw_data['Qual o tipo de instalação portuária à qual você está vinculado'].value_counts().to_dict(),
            'states': self.raw_data['Estado da Federação (UF)'].value_counts().to_dict(),
            'departments': self.raw_data['Área_Departamento organizacional'].value_counts().to_dict()
        }
        
        return metadata
    
    def process_risk_data(self) -> pd.DataFrame:
        """
        Process risk assessment data into structured format.
        
        Returns:
            Processed DataFrame with risk data in long format
        """
        if self.raw_data is None:
            self.load_data()
            
        df = self.clean_column_names()
        
        # Initialize list to store processed risk data
        risk_records = []
        
        # Process each row (each response)
        for idx, row in df.iterrows():
            # Extract basic information
            response_info = {
                'timestamp': row.get('Carimbo de data_hora'),
                'port_type': row.get('Qual o tipo de instalação portuária à qual você está vinculado'),
                'state': row.get('Estado da Federação (UF)'),
                'department': row.get('Área_Departamento organizacional')
            }
            
            # Process risk categories
            for category, risk_numbers in self.risk_categories.items():
                for risk_num in risk_numbers:
                    # Process each time period for this risk
                    for period_name, period_suffix in self.time_periods.items():
                        # Construct column name
                        col_pattern = f"{risk_num}.*{period_suffix}"
                        matching_cols = [col for col in df.columns if re.search(col_pattern, col, re.IGNORECASE)]
                        
                        if matching_cols:
                            col_name = matching_cols[0]
                            risk_value = row.get(col_name)
                            
                            if pd.notna(risk_value) and risk_value != '':
                                # Extract risk description from column name
                                risk_desc = self._extract_risk_description(col_name)
                                
                                risk_record = response_info.copy()
                                risk_record.update({
                                    'risk_category': category,
                                    'risk_number': risk_num,
                                    'risk_description': risk_desc,
                                    'time_period': period_name,
                                    'risk_score': int(risk_value) if str(risk_value).isdigit() else risk_value
                                })
                                risk_records.append(risk_record)
        
        # Create processed DataFrame
        self.processed_data = pd.DataFrame(risk_records)
        logger.info(f"Processed {len(self.processed_data)} risk records")
        
        return self.processed_data
    
    def _extract_risk_description(self, column_name: str) -> str:
        """
        Extract risk description from column name.
        
        Args:
            column_name: Raw column name from Excel
            
        Returns:
            Cleaned risk description
        """
        # Remove risk number and time period
        desc = re.sub(r'^\d+\.\d+\s*', '', column_name)
        desc = re.sub(r'\s*\[.*?\]\s*$', '', desc)
        desc = re.sub(r'_+', ' ', desc)
        return desc.strip()
    
    def calculate_risk_statistics(self) -> Dict[str, Any]:
        """
        Calculate risk statistics and aggregations.
        
        Returns:
            Dictionary containing risk statistics
        """
        if self.processed_data is None:
            self.process_risk_data()
        
        # Filter only numeric risk scores
        numeric_data = self.processed_data[
            self.processed_data['risk_score'].apply(lambda x: isinstance(x, (int, float)))
        ].copy()
        
        stats = {
            'overall_risk_levels': {
                category: numeric_data[numeric_data['risk_category'] == category]['risk_score'].mean()
                for category in self.risk_categories.keys()
            },
            'risk_by_port_type': {},
            'risk_by_state': {},
            'risk_by_time_period': {},
            'top_risks': {},
            'risk_trends': {}
        }
        
        # Calculate by port type
        for port_type in numeric_data['port_type'].unique():
            if pd.notna(port_type):
                port_data = numeric_data[numeric_data['port_type'] == port_type]
                stats['risk_by_port_type'][port_type] = {
                    category: port_data[port_data['risk_category'] == category]['risk_score'].mean()
                    for category in self.risk_categories.keys()
                }
        
        # Calculate by state
        for state in numeric_data['state'].unique():
            if pd.notna(state):
                state_data = numeric_data[numeric_data['state'] == state]
                stats['risk_by_state'][state] = state_data['risk_score'].mean()
        
        # Calculate by time period
        for period in numeric_data['time_period'].unique():
            period_data = numeric_data[numeric_data['time_period'] == period]
            stats['risk_by_time_period'][period] = {
                category: period_data[period_data['risk_category'] == category]['risk_score'].mean()
                for category in self.risk_categories.keys()
            }
        
        # Top risks by category
        for category in self.risk_categories.keys():
            category_data = numeric_data[numeric_data['risk_category'] == category]
            top_risks = category_data.groupby('risk_description')['risk_score'].mean().sort_values(ascending=False)
            stats['top_risks'][category] = top_risks.head(10).to_dict()
        
        return stats
    
    def get_risk_matrix_data(self) -> Dict[str, pd.DataFrame]:
        """
        Prepare data for risk matrix visualization.
        
        Returns:
            Dictionary with DataFrames for different risk matrix views
        """
        if self.processed_data is None:
            self.process_risk_data()
        
        numeric_data = self.processed_data[
            self.processed_data['risk_score'].apply(lambda x: isinstance(x, (int, float)))
        ].copy()
        
        matrices = {}
        
        # Overall risk matrix by category and time period
        matrices['overall'] = numeric_data.pivot_table(
            values='risk_score',
            index='risk_category',
            columns='time_period',
            aggfunc='mean'
        )
        
        # Risk matrix by port type
        for port_type in numeric_data['port_type'].unique():
            if pd.notna(port_type):
                port_data = numeric_data[numeric_data['port_type'] == port_type]
                matrices[f'port_type_{port_type}'] = port_data.pivot_table(
                    values='risk_score',
                    index='risk_category',
                    columns='time_period',
                    aggfunc='mean'
                )
        
        return matrices
    
    def export_processed_data(self, output_path: str = 'outputs/processed_data.csv') -> None:
        """
        Export processed data to CSV.
        
        Args:
            output_path: Path to save the processed data
        """
        if self.processed_data is None:
            self.process_risk_data()
        
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.processed_data.to_csv(output_path, index=False)
        logger.info(f"Processed data exported to {output_path}")

# Main execution for testing
if __name__ == "__main__":
    processor = PortRiskDataProcessor()
    
    # Load and process data
    processor.load_data()
    metadata = processor.extract_metadata()
    processed_data = processor.process_risk_data()
    statistics = processor.calculate_risk_statistics()
    
    print("Data Processing Summary:")
    print(f"Total responses: {metadata['total_responses']}")
    print(f"Processed risk records: {len(processed_data)}")
    print(f"Risk categories: {list(processed_data['risk_category'].unique())}")
    
    # Export processed data
    processor.export_processed_data()
