#!/usr/bin/env python3
"""
Test script to verify the backend is working correctly.
"""

import requests
import json

def test_backend():
    """Test the backend API endpoints."""
    base_url = "http://localhost:5000"
    
    # Test data
    test_data = {
        "targetName": "Test Object",
        "category": "Super-Jupiter",
        "carbonRatio": "88 ± 13",
        "oxygenRatio": "683 ± 53",
        "instrument": "VLT/CRIRES+",
        "reference": "Test et al. 2024",
        "notes": "Test submission",
        "submitterEmail": "test@example.com"
    }
    
    try:
        # Test submission endpoint
        print("Testing submission endpoint...")
        response = requests.post(f"{base_url}/api/submit", json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend server.")
        print("Make sure the Flask server is running on port 5000.")
        print("Run: python start_server.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend()
