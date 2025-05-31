import os
import requests
import urllib3

#gateway_url = os.getenv("AAP_GATEWAY_URL")
#token = os.getenv("AAP_TOKEN")
gateway_url = "https://ec2-18-222-140-65.us-east-2.compute.amazonaws.com"
token="BSHASw6Q0wK3BF0GRHtrVHTQkVTEb5"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Your logic here, just like in previous response
import requests

# Inputs
#gateway_url = "https://your-aap-gateway-url"
#token = "your_aap_token"
#headers = {
#    "Authorization": f"Bearer {token}",
#    "Content-Type": "application/json",
#}

# Config
org_id = 1  # Replace with actual Organization ID
credential_id = 4  # Replace with actual SCM credential ID
project_name = "demo-project"
inventory_name = "demo-inventory"
git_url = "git@github.com:kamlendu1982/caac-aap-2.5.git"
inventory_relative_path = "inventory.yml"  # Path inside repo

# Step 1: Create Project
project_payload = {
    "name": project_name,
    "description": "Project with Git-sourced inventory",
    "organization": org_id,
    "scm_type": "git",
    "scm_url": git_url,
    "scm_branch": "main",
    "credential": credential_id,
    "scm_update_on_launch": True,
}

project_resp = requests.post(
    f"{gateway_url}/api/controller/v2/projects/", headers=headers, json=project_payload, verify=False
)
project_resp.raise_for_status()
project_id = project_resp.json()["id"]
print(f"Created Project ID: {project_id}")

# Step 2: Create Inventory
inventory_payload = {
    "name": inventory_name,
    "description": "Inventory sourced from Git project",
    "organization": org_id,
}

inventory_resp = requests.post(
    f"{gateway_url}/api/controller/v2/inventories/", headers=headers, json=inventory_payload, verify=False
)
inventory_resp.raise_for_status()
inventory_id = inventory_resp.json()["id"]
print(f"Created Inventory ID: {inventory_id}")

# Step 3: Create Inventory Source (linking project to inventory)
inventory_source_payload = {
    "name": "Git Inventory Source",
    "source": "scm",
    "inventory": inventory_id,
    "source_project": project_id,
    "source_path": inventory_relative_path,
    "update_on_launch": True,
}

inv_src_resp = requests.post(
    f"{gateway_url}/api/controller/v2/inventory_sources/",
    headers=headers,
    json=inventory_source_payload,
    verify=False
)
inv_src_resp.raise_for_status()
inv_src_id = inv_src_resp.json()["id"]
print(f"Created Inventory Source ID: {inv_src_id}")

