#!/usr/bin/env python3
"""
Script to export approved measurements from the database to CSV format
for integration with the main isotope ratios table.
"""

import sqlite3
import csv
import json
from datetime import datetime
from typing import List, Dict

DATABASE = 'isotope_submissions.db'

def get_approved_measurements() -> List[Dict]:
    """Retrieve all approved measurements from the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM approved_measurements 
        ORDER BY approved_at DESC
    ''')
    
    measurements = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return measurements

def export_to_csv(measurements: List[Dict], filename: str = 'approved_measurements.csv') -> None:
    """Export approved measurements to CSV file."""
    if not measurements:
        print("No approved measurements to export.")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id', 'submission_id', 'target_name', 'category', 'carbon_ratio', 
            'oxygen_ratio', 'instrument', 'reference', 'notes', 'approved_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for measurement in measurements:
            # Convert datetime to string for CSV
            measurement_copy = measurement.copy()
            if measurement_copy['approved_at']:
                measurement_copy['approved_at'] = measurement_copy['approved_at']
            writer.writerow(measurement_copy)
    
    print(f"Exported {len(measurements)} approved measurements to {filename}")

def generate_html_table_rows(measurements: List[Dict]) -> str:
    """Generate HTML table rows for approved measurements."""
    if not measurements:
        return ""
    
    # Category mapping for CSS classes
    category_classes = {
        'Super-Jupiter': 'category-super-jupiter',
        'Young Brown Dwarf': 'category-young-brown-dwarf',
        'Brown Dwarf': 'category-brown-dwarf',
        'Star': 'category-star'
    }
    
    # Instrument mapping for CSS classes
    instrument_classes = {
        'VLT/CRIRES+': 'instrument-text-crires',
        'Keck/NIRSPEC': 'instrument-text-keck-nirspec',
        'Keck/KPIC': 'instrument-text-kpic',
        'JWST/NIRSpec': 'instrument-text-jwst-nirspec'
    }
    
    rows = []
    for measurement in measurements:
        category_class = category_classes.get(measurement['category'], '')
        instrument_class = instrument_classes.get(measurement['instrument'], 'instrument-text-other')
        
        # Format oxygen ratio
        oxygen_ratio = measurement['oxygen_ratio'] if measurement['oxygen_ratio'] else '—'
        
        # Format instrument
        instrument = measurement['instrument'] if measurement['instrument'] else '—'
        if instrument != '—':
            instrument = f'<span class="{instrument_class}">{instrument}</span>'
        
        # Format notes
        notes = measurement['notes'] if measurement['notes'] else '—'
        
        row = f'''\t\t\t\t\t<tr class="{category_class}">
\t\t\t\t\t\t<td><strong>{measurement['target_name']}</strong></td>
\t\t\t\t\t\t<td>{measurement['category'] or '—'}</td>
\t\t\t\t\t\t<td>{measurement['carbon_ratio']}</td>
\t\t\t\t\t\t<td>{oxygen_ratio}</td>
\t\t\t\t\t\t<td>{instrument}</td>
\t\t\t\t\t\t<td><a href="#" class="doi-link" target="_blank">{measurement['reference']}</a></td>
\t\t\t\t\t\t<td>{notes}</td>
\t\t\t\t\t</tr>'''
        
        rows.append(row)
    
    return '\n'.join(rows)

def main():
    """Main function to export approved measurements."""
    print("Exporting approved measurements...")
    
    try:
        measurements = get_approved_measurements()
        
        if measurements:
            # Export to CSV
            export_to_csv(measurements)
            
            # Generate HTML for manual integration
            html_rows = generate_html_table_rows(measurements)
            
            print("\n" + "="*50)
            print("HTML TABLE ROWS FOR MANUAL INTEGRATION:")
            print("="*50)
            print(html_rows)
            print("="*50)
            
            print(f"\nFound {len(measurements)} approved measurements.")
            print("You can copy the HTML rows above and paste them into your isotope_ratios.html table.")
            
        else:
            print("No approved measurements found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
