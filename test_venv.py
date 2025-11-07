"""
Test script to verify virtual environment and dependencies
"""

import sys

def test_environment():
    print("VIRTUAL ENVIRONMENT TEST")
    print("=" * 40)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Test required packages
    required_packages = [
        'pandas', 'numpy', 'plotly', 'dash', 
        'dash_bootstrap_components', 'openpyxl'
    ]
    
    print("\nTesting package imports:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package} - {e}")
    
    # Test data loading
    try:
        import pandas as pd
        print(f"\nTesting data loading:")
        df = pd.read_excel('questionario.xlsx')
        print(f"✓ Data loaded successfully")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  First row timestamp: {df.iloc[0, 0] if not df.empty else 'No data'}")
        
        # Show first few column names
        print(f"\nFirst 5 column names:")
        for i, col in enumerate(df.columns[:5]):
            print(f"  {i+1}. {col}")
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
    
    print("\n" + "=" * 40)
    print("Environment test complete!")

if __name__ == "__main__":
    test_environment()
