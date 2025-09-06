#!/usr/bin/env python3
"""
Automated script to update isotope_ratios.html with data from isotope_ratios.csv
Properly formats uncertainties and maintains HTML structure.
"""

import csv
import re
from typing import List, Dict
from datetime import datetime


def parse_uncertainty(value_str: str) -> str:
    """
    Parse uncertainty string and format for HTML display.
    
    Examples:
    - "88 (13)" -> "88 ± 13"
    - "97 (+25 / -18)" -> "97<sup>+25</sup><sub>-18</sub>"
    - "81^{+28}_{-19}" -> "81<sup>+28</sup><sub>-19</sub>"
    - "184^{+61}_{-40}" -> "184<sup>+61</sup><sub>-40</sub>"
    """
    value_str = value_str.strip()
    
    # Handle symmetric uncertainties: "88 (13)"
    symmetric_match = re.match(r'(\d+)\s*\((\d+)\)', value_str)
    if symmetric_match:
        value, uncertainty = symmetric_match.groups()
        return f"{value} ± {uncertainty}"
    
    # Handle asymmetric uncertainties with parentheses: "97 (+25 / -18)"
    asym_paren_match = re.match(r'(\d+)\s*\(\+(\d+)\s*/\s*-(\d+)\)', value_str)
    if asym_paren_match:
        value, upper, lower = asym_paren_match.groups()
        return f"{value}<sup>+{upper}</sup><sub>-{lower}</sub>"
    
    # Handle LaTeX-style asymmetric uncertainties: "81^{+28}_{-19}"
    latex_match = re.match(r'(\d+)\^\{?\+(\d+)\}?_\{?-(\d+)\}?', value_str)
    if latex_match:
        value, upper, lower = latex_match.groups()
        return f"{value}<sup>+{upper}</sup><sub>-{lower}</sub>"
    
    # Handle cases with additional notes: "114^{+69}_{-33} (≈2σ)"
    latex_note_match = re.match(r'(\d+)\^\{?\+(\d+)\}?_\{?-(\d+)\}?\s*\(([^)]+)\)', value_str)
    if latex_note_match:
        value, upper, lower, note = latex_note_match.groups()
        return f"{value}<sup>+{upper}</sup><sub>-{lower}</sub> ({note})"
    
    # Return as-is if no pattern matches
    return value_str


def get_category_class(category: str) -> str:
    """Get CSS class for category color coding."""
    category_lower = category.lower().strip()
    
    if 'super-jupiter' in category_lower:
        return 'category-super-jupiter'
    elif 'young brown dwarf' in category_lower:
        return 'category-young-brown-dwarf'
    elif 'brown dwarf' in category_lower:
        return 'category-brown-dwarf'
    elif any(stellar in category_lower for stellar in ['star', 'k6', 'm7', 'host-star', 'companion']):
        return 'category-star'
    else:
        return 'category-brown-dwarf'  # default


def get_instrument_class(instrument: str) -> str:
    """Get CSS class for instrument color coding."""
    instrument_lower = instrument.lower().strip()
    
    if 'crires' in instrument_lower:
        return 'instrument-crires'
    elif 'nirspec' in instrument_lower and 'keck' in instrument_lower:
        return 'instrument-keck-nirspec'
    elif 'kpic' in instrument_lower or ('keck' in instrument_lower and 'kpic' in instrument_lower):
        return 'instrument-kpic'
    elif 'jwst' in instrument_lower and 'nirspec' in instrument_lower:
        return 'instrument-jwst-nirspec'
    else:
        return 'instrument-other'  # default for unknown instruments


def format_target_name(target: str) -> str:
    """Format target name with proper emphasis and abbreviations."""
    target = target.strip()
    
    # Handle cases with abbreviations in parentheses
    if '(' in target and ')' in target:
        parts = target.split('(')
        main_name = parts[0].strip()
        abbrev = '(' + parts[1]
        return f"<strong>{main_name}</strong><br><small>{abbrev}</small>"
    else:
        return f"<strong>{target}</strong>"


def format_doi_link(reference: str, doi: str) -> str:
    """Create properly formatted DOI link."""
    if doi and doi.lower() != 'none' and doi.strip():
        doi_clean = doi.strip()
        if not doi_clean.startswith('http'):
            doi_url = f"https://doi.org/{doi_clean}"
        else:
            doi_url = doi_clean
        return f'<a href="{doi_url}" class="doi-link" target="_blank">{reference}</a>'
    else:
        return reference


def format_chemical_formula(text: str) -> str:
    """Format chemical formulas with proper superscripts and subscripts."""
    # Handle H_2^{18}O patterns
    text = re.sub(r'H_(\d+)\^{(\d+)}O', r'H<sub>\1</sub><sup>\2</sup>O', text)
    
    # Handle other common chemical notation patterns
    text = re.sub(r'\^{(\d+)}', r'<sup>\1</sup>', text)  # ^{18} -> <sup>18</sup>
    text = re.sub(r'_(\d+)', r'<sub>\1</sub>', text)     # _2 -> <sub>2</sub>
    
    return text


def clean_measurement(measurement: str) -> str:
    """Clean and format measurement values, including proper uncertainty parsing."""
    measurement = measurement.strip()
    
    if measurement.lower() in ['none', 'none reported', '—', '-']:
        return '—'
    
    # Handle chemical formulas first
    measurement = format_chemical_formula(measurement)
    
    # Handle tentative detections with possible uncertainties
    if 'tentative' in measurement.lower():
        # Check if there are uncertainties in the tentative detection string
        # Example: "tentative 18O detection (2.1σ)"
        return measurement.replace('tentative', 'Tentative')
    
    # Try to parse uncertainties in oxygen measurements too
    # Look for patterns like "288^{+125}_{-70}" or "240^{+145}_{-80}"
    uncertainty_parsed = parse_uncertainty(measurement)
    if uncertainty_parsed != measurement:
        return uncertainty_parsed
    
    return measurement


def read_csv_data(csv_file: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of dictionaries."""
    data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean keys and values
            clean_row = {}
            for key, value in row.items():
                clean_key = key.strip()
                clean_value = value.strip() if value else ''
                clean_row[clean_key] = clean_value
            data.append(clean_row)
    return data


def generate_table_rows(csv_file: str) -> str:
    """Generate HTML table rows from CSV data."""
    data = read_csv_data(csv_file)
    
    rows_html = []
    
    for row in data:
        target = format_target_name(row['target'])
        category = row['category'].strip()
        category_class = get_category_class(category)
        
        # Format measurements
        carbon_ratio = parse_uncertainty(str(row['12C/13C']))
        oxygen_ratio = clean_measurement(str(row['16O/18O']))
        
        instrument = row['instrument'].strip()
        instrument_class = get_instrument_class(instrument)
        instrument_text_class = instrument_class.replace('instrument-', 'instrument-text-')
        reference = row['reference'].strip()
        doi = row.get('doi', '').strip()
        note = row.get('note', '').strip() if row.get('note', '').strip() else '—'
        
        # Create DOI link
        reference_link = format_doi_link(reference, doi)
        
        # Format category display
        if 'host-star' in category.lower():
            category_display = 'Star (K6)'
        elif 'companion' in category.lower():
            category_display = 'Star (M7)'
        else:
            category_display = category.title()
        
        # Generate row HTML with only category class (no instrument border)
        row_html = f'''									<tr class="{category_class}">
										<td>{target}</td>
										<td>{category_display}</td>
										<td>{carbon_ratio}</td>
										<td>{oxygen_ratio}</td>
										<td><span class="{instrument_text_class}">{instrument}</span></td>
										<td>{reference_link}</td>
										<td>{note}</td>
									</tr>'''
        
        rows_html.append(row_html)
    
    return '\n'.join(rows_html)


def generate_csv_viewer_html(csv_file: str) -> str:
    """Generate HTML page for viewing and downloading the raw CSV data."""
    data = read_csv_data(csv_file)
    
    # Create CSV viewer HTML
    csv_viewer_html = f'''<!DOCTYPE HTML>
<html>
<head>
    <title>Raw Isotope Data (CSV) - Darío González Picos</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .download-section {{
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: #e8f4fd;
            border-radius: 8px;
        }}
        .download-button {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 0 10px;
            transition: transform 0.2s ease;
        }}
        .download-button:hover {{
            transform: translateY(-2px);
            text-decoration: none;
            color: white;
        }}
        .csv-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9rem;
        }}
        .csv-table th, .csv-table td {{
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        .csv-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }}
        .csv-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .csv-table tr:hover {{
            background-color: #e8f4fd;
        }}
        .back-link {{
            display: inline-block;
            margin: 20px 0;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 768px) {{
            .csv-table {{
                font-size: 0.8rem;
            }}
            .csv-table th, .csv-table td {{
                padding: 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="isotope_ratios.html" class="back-link">← Back to Formatted Table</a>
        
        <h1>Raw Isotope Ratios Data (CSV Format)</h1>
        
        <div class="download-section">
            <p><strong>Download CSV Data:</strong></p>
            <a href="isotope_ratios.csv" download class="download-button">📥 Download CSV File</a>
        </div>
        
        <div style="overflow-x: auto;">
            <table class="csv-table">
                <thead>
                    <tr>'''
    
    # Add headers
    if data:
        for header in data[0].keys():
            csv_viewer_html += f'\n                        <th>{header}</th>'
    
    csv_viewer_html += '''
                    </tr>
                </thead>
                <tbody>'''
    
    # Add data rows
    for row in data:
        csv_viewer_html += '\n                    <tr>'
        for value in row.values():
            csv_viewer_html += f'\n                        <td>{value if value else "—"}</td>'
        csv_viewer_html += '\n                    </tr>'
    
    csv_viewer_html += f'''
                </tbody>
            </table>
        </div>
        
        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <p><strong>About this data:</strong></p>
            <ul>
                <li>This table shows the raw CSV data used to generate the formatted isotope ratios table</li>
                <li>Total entries: {len(data)}</li>
                <li>Last updated: {datetime.now().strftime('%Y-%m-%d')}</li>
                <li>You can download this data in CSV format using the buttons above</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
    
    return csv_viewer_html


def generate_csv_data_uri(data: List[Dict[str, str]]) -> str:
    """Generate a data URI for CSV download."""
    import urllib.parse
    
    if not data:
        return ""
    
    # Create CSV content
    csv_content = ",".join(data[0].keys()) + "\\n"
    for row in data:
        csv_content += ",".join(f'"{value}"' for value in row.values()) + "\\n"
    
    # URL encode the CSV content
    return urllib.parse.quote(csv_content)


def update_html_file(html_file: str, csv_file: str) -> None:
    """Update the HTML file with new table content and current date."""
    # Generate new table rows
    new_rows = generate_table_rows(csv_file)
    
    # Get current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Read the current HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the table body section and replace it
    tbody_pattern = r'(<tbody>\s*)(.*?)(\s*</tbody>)'
    
    def replace_tbody(match):
        return f"{match.group(1)}\n{new_rows}\n{match.group(3)}"
    
    updated_content = re.sub(tbody_pattern, replace_tbody, html_content, flags=re.DOTALL)
    
    # Update the last updated date
    date_pattern = r'(Last updated:\s*)(\d{4}-\d{2}-\d{2})'
    updated_content = re.sub(date_pattern, rf'\g<1>{current_date}', updated_content)
    
    # Write the updated content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    # Generate CSV viewer page
    csv_viewer_content = generate_csv_viewer_html(csv_file)
    csv_viewer_file = csv_file.replace('.csv', '_viewer.html')
    with open(csv_viewer_file, 'w', encoding='utf-8') as f:
        f.write(csv_viewer_content)
    
    print(f"Successfully updated {html_file} with data from {csv_file}")
    print(f"Generated CSV viewer at {csv_viewer_file}")
    print(f"Updated date to: {current_date}")


def main():
    """Main function to update the isotope ratios table."""
    csv_file = '/home/picos/public_html/isotope_ratios.csv'
    html_file = '/home/picos/public_html/isotope_ratios.html'
    
    try:
        update_html_file(html_file, csv_file)
        print("Table update completed successfully!")
        
        # Print summary of processed data
        data = read_csv_data(csv_file)
        print(f"\nProcessed {len(data)} entries:")
        for row in data:
            print(f"  - {row['target']}: {parse_uncertainty(str(row['12C/13C']))}")
            
    except Exception as e:
        print(f"Error updating table: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
