import json
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import app

def export():
    print("Exporting OpenAPI spec...")
    openapi_data = app.openapi()
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_data, f, indent=2)
    print(f"openapi.json exported successfully to {output_path}")

if __name__ == "__main__":
    export()
