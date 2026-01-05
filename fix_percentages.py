import re
import sys

def fix_percentages(filepath):
    """Fix percentage formatting by rounding to whole numbers"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match percentages with decimals (e.g., 28,8% or 28.8%)
    # We need to round the number and replace
    pattern = r'(\d+[.,]\d+)%'
    
    def replacer(match):
        percentage = match.group()
        # Extract the number
        num_str = percentage[:-1]  # Remove the %
        
        # Handle both comma and decimal point
        if ',' in num_str:
            num = float(num_str.replace(',', '.'))
        else:
            num = float(num_str)
        
        # Round to nearest whole number
        rounded = round(num)
        
        # Replace with the same separator style (comma for Brazilian format)
        if ',' in percentage:
            return f'{rounded}%'
        else:
            return f'{rounded}%'
    
    new_content = re.sub(pattern, replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed percentages in {filepath}")

if __name__ == '__main__':
    fix_percentages('quarto/ambiental.qmd')
    fix_percentages('quarto/economic.qmd')
    fix_percentages('quarto/geopolitico.qmd')
    fix_percentages('quarto/social.qmd')
    fix_percentages('quarto/tecnologico.qmd')
    fix_percentages('quarto/sumario-executivo.qmd')
    fix_percentages('quarto/interconexao-riscos.qmd')
    print("All files processed!")
