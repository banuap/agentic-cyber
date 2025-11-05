import pandas as pd
import openpyxl
import json

# File path
excel_file = r'C:\Users\banu.parasuraman\Downloads\SailPoint_Onboarding_Application_Questionnaire_v2.xlsx'

# Load the workbook
wb = openpyxl.load_workbook(excel_file)

print("=" * 80)
print("EXCEL FILE ANALYSIS: SailPoint Application Onboarding Template")
print("=" * 80)

# Get all sheet names
sheet_names = wb.sheetnames
print(f"\nTotal Sheets: {len(sheet_names)}")
print(f"Sheet Names: {sheet_names}\n")

# Analyze each sheet
analysis = {}

for sheet_name in sheet_names:
    print("=" * 80)
    print(f"SHEET: {sheet_name}")
    print("=" * 80)
    
    # Read with pandas
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Basic info
    print(f"\nDimensions: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"\nColumns: {list(df.columns)}")
    
    # Show first few rows
    print(f"\nFirst 5 rows:")
    print(df.head().to_string())
    
    # Check for empty cells
    empty_cells = df.isnull().sum()
    if empty_cells.sum() > 0:
        print(f"\nEmpty/Missing cells per column:")
        print(empty_cells[empty_cells > 0])
    
    # Store analysis
    analysis[sheet_name] = {
        'dimensions': df.shape,
        'columns': list(df.columns),
        'sample_data': df.head(3).to_dict('records'),
        'empty_cells': empty_cells.to_dict()
    }
    
    print("\n")

# Save analysis to JSON
output_file = r'C:\Users\banu.parasuraman\Downloads\agentic-cyber\excel_analysis.json'
with open(output_file, 'w') as f:
    json.dump(analysis, f, indent=2, default=str)

print("=" * 80)
print(f"Analysis saved to: {output_file}")
print("=" * 80)
