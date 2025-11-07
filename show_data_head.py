"""
Script to display the head of the raw and processed data
"""

import pandas as pd
from data_processor import PortRiskDataProcessor

def show_data_head():
    """Display the head of raw and processed data"""
    
    print("PORT RISK ASSESSMENT DATA OVERVIEW")
    print("=" * 60)
    
    # Initialize processor and load data
    processor = PortRiskDataProcessor()
    
    try:
        processor.load_data()
        
        # Show raw data
        print("\nRAW DATA HEAD:")
        print("=" * 40)
        print(f"Shape: {processor.raw_data.shape}")
        print(f"Columns: {len(processor.raw_data.columns)}")
        print("\nFirst 5 rows:")
        print(processor.raw_data.head())
        
        print("\nCOLUMN NAMES:")
        print("=" * 40)
        for i, col in enumerate(processor.raw_data.columns):
            print(f"{i+1:2d}. {col}")
            if i >= 19:  # Show first 20 columns
                print(f"... and {len(processor.raw_data.columns) - 20} more columns")
                break
        
        # Show metadata
        metadata = processor.extract_metadata()
        print(f"\nMETADATA:")
        print("=" * 40)
        print(f"Total responses: {metadata['total_responses']}")
        print(f"Date range: {metadata['date_range']['start']} to {metadata['date_range']['end']}")
        print(f"States: {list(metadata['states'].keys())}")
        print(f"Port types: {list(metadata['port_types'].keys())}")
        
        # Process data
        processed_data = processor.process_risk_data()
        
        print(f"\nPROCESSED DATA HEAD:")
        print("=" * 40)
        print(f"Shape: {processed_data.shape}")
        print(f"Columns: {list(processed_data.columns)}")
        print("\nFirst 10 rows:")
        print(processed_data.head(10))
        
        # Show unique values
        print(f"\nUNIQUE VALUES IN PROCESSED DATA:")
        print("=" * 40)
        print(f"Risk categories: {processed_data['risk_category'].unique()}")
        print(f"Time periods: {processed_data['time_period'].unique()}")
        print(f"Port types: {processed_data['port_type'].unique()}")
        print(f"States: {processed_data['state'].unique()}")
        
        # Show sample risk descriptions
        print(f"\nSAMPLE RISK DESCRIPTIONS:")
        print("=" * 40)
        sample_risks = processed_data['risk_description'].unique()[:10]
        for i, risk in enumerate(sample_risks, 1):
            print(f"{i}. {risk}")
        
        # Show risk score distribution
        print(f"\nRISK SCORE DISTRIBUTION:")
        print("=" * 40)
        numeric_data = processed_data[
            processed_data['risk_score'].apply(lambda x: isinstance(x, (int, float)))
        ]
        if not numeric_data.empty:
            score_dist = numeric_data['risk_score'].value_counts().sort_index()
            for score, count in score_dist.items():
                print(f"Score {score}: {count} occurrences")
            print(f"Mean score: {numeric_data['risk_score'].mean():.2f}")
            print(f"Std deviation: {numeric_data['risk_score'].std():.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure 'questionario.xlsx' exists in the current directory.")

if __name__ == "__main__":
    show_data_head()
