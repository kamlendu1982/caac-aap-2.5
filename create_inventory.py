import requests
import json
import urllib3
import os
import time

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

gateway_url = os.getenv("AAP_GATEWAY_URL")
token = os.getenv("AAP_TOKEN")
github_user = os.getenv("SCM_USER")
github_token = os.getenv("SCM_TOKEN")
execution_env_id = os.getenv("EXE_ENV_ID")
execution_env_id = 9
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# GitHub credential creation
def create_github_credential():
    url = f"{gateway_url}/api/controller/v2/credentials/"
    payload = {
        "name": "GitHubControlKamPAT",
        "description": "GitHub token for project sync",
        "organization": 1,  # Adjust this ID to your org
        "credential_type": 2,  # 2 = Source Control
        "inputs": {
            "username": github_user,
            "password": github_token
        }
    }
    response = requests.post(url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.json()["id"]

# Project creation
def create_project(credential_id):
    url = f"{gateway_url}/api/controller/v2/projects/"
    payload = {
        "name": "Infra_caac",
        "description": "Infra CAAC deployment project",
        "organization": 1,  # Adjust org ID
        "scm_type": "git",
        "scm_url": "https://github.com/kamlendu1982/caac-aap-2.5.git",
        "scm_branch": "main",
        "credential": credential_id,
        "scm_update_on_launch": True
    }
    response = requests.post(url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.json()["id"]

# Inventory creation
def create_inventory(project_id):
    url = f"{gateway_url}/api/controller/v2/inventories/"
    payload = {
        "name": "Inventory_Infra_caac",
        "description": "Dynamic inventory",
        "organization": 1  # Adjust org ID
    }
    response = requests.post(url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.json()["id"]

# Create Inventory Source (linking project to inventory)
def create_inventory_source(project_id, inventory_id, inventory_relative_path):
    inventory_source_payload = {
      "name": "Inventory_Infra_caa Source",
      "source": "scm",
      "inventory": inventory_id,
      "source_project": project_id,
      "source_path": inventory_relative_path,
      "update_on_launch": True,
    }
    response = requests.post(
      f"{gateway_url}/api/controller/v2/inventory_sources/",
      headers=headers,
      json=inventory_source_payload,
      verify=False
    )
    response.raise_for_status()
    return response.json()["id"]

def get_execution_environment_id(name):
    url = f"{gateway_url}/api/controller/v2/execution_environments/?name={name}"
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise Exception(f"Execution Environment '{name}' not found.")
    return results[0]["id"]

def create_job_template(project_id, inventory_id):
    payload = {
        "name": "Create_CAAC_AAP",
        "description": "Runs a job using repo and dynamic inventory",
        "job_type": "run",
        "inventory": inventory_id,
        "project": project_id,
        "playbook": "playbooks/aap_config.yml",  
        #"execution_environment": get_execution_environment_id("ee-supported-rhel9_caac_infra"),
        "execution_environment": execution_env_id,
        "limit": "localhost",
        "webhook_service": "GitHub",
        "verbosity": 1
    }
    print(payload)
    response = requests.post(f"{gateway_url}/api/controller/v2/job_templates/", headers=headers, json=payload, verify=False)
    print(response.text)
    response.raise_for_status()
    return response.json()["id"]

# Run the workflow
if __name__ == "__main__":
    github_cred_id = create_github_credential()
    project_id = create_project(github_cred_id)
    time.sleep(15)
    inventory_id = create_inventory(project_id)
    inventory_source = create_inventory_source(project_id, inventory_id, "inventory.yml")
    print(f"GitHub Credential ID: {github_cred_id}")
    print(f"Project ID: {project_id}")
    print(f"Inventory ID: {inventory_id}")
    job_template_id = create_job_template(int(project_id), int(inventory_id))
    #job_template_id = create_job_template(34, 10)
    url = f"{gateway_url}/api/controller/v2/job_templates/{job_template_id}/launch/"
    response = requests.post(url, headers=headers, verify=False)

