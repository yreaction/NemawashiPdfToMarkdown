#!/usr/bin/env python
"""
Example script to demonstrate how to use the PDF to Markdown service with Docker.
This script shows how to interact with the service once it's running in Docker.
"""

import requests
import json
import os
import sys

# Service URL (when running in Docker)
SERVICE_URL = "http://localhost:8002/extract_markdown"

def convert_pdf_to_markdown(pdf_path):
    """
    Send a request to the PDF to Markdown service to convert a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file to convert
    
    Returns:
        str: The markdown content if successful, None otherwise
    """
    # When using Docker, the path needs to be adjusted to the container's path
    # If the file is in the ./data directory, it will be mounted to /app/data in the container
    if os.path.exists(pdf_path):
        # Get the absolute path and convert to Docker path if needed
        abs_path = os.path.abspath(pdf_path)
        
        # If using local path in data directory, convert to Docker path
        if "data" in abs_path:
            # Extract the filename
            filename = os.path.basename(abs_path)
            # Use the Docker container path
            docker_path = f"/app/data/{filename}"
            request_path = docker_path
        else:
            # Use the original path (for testing outside Docker)
            request_path = abs_path
        
        # Prepare the request
        payload = {"file_path": request_path}
        headers = {"Content-Type": "application/json"}
        
        try:
            # Send the request to the service
            response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                return result["markdown_content"]
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error connecting to the service: {e}")
            return None
    else:
        print(f"Error: File not found - {pdf_path}")
        return None

def main():
    """Main function to demonstrate the usage."""
    if len(sys.argv) < 2:
        print("Usage: python docker-usage-example.py <path_to_pdf_file>")
        print("Example: python docker-usage-example.py ./data/example.pdf")
        return
    
    pdf_path = sys.argv[1]
    print(f"Converting PDF: {pdf_path}")
    
    markdown_content = convert_pdf_to_markdown(pdf_path)
    
    if markdown_content:
        print("\nConversion successful! Markdown content:")
        print("-" * 50)
        print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)
        print("-" * 50)
        print(f"Full markdown content will be available in the output directory.")

if __name__ == "__main__":
    main()
