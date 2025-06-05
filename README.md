# caac-aap-2.5

# Configuration as Code for Ansible Automation Platform (AAP) 2.5

This repository provides a starting point for implementing **Configuration as Code (CaC)** for **Ansible Automation Platform 2.5**.
You can follow the steps below to use this setup. The order can be automated or adjusted to suit your environment.

---

## 🛠️ Setup Steps

### 1. Build an Execution Environment

- Navigate to the `execution-environment/` folder. It contains:
  - `requirements.yml`
  - `execution-environment.yml`
- Ensure a valid `ansible.cfg` file is included in the build context.
- Build the image using the following command:

  ```bash
  ansible-builder build -t infra_caac_rhel9

    Alternatively, you can use a Dockerfile or Containerfile to build the image.

### 2. Push the Image to Automation Hub
Use podman or docker to push the built image to your private or Red Hat Automation Hub:
podman push infra_caac_rhel9 <automation-hub-url>/infra_caac_rhel9

### 3. Create Execution Environment in AAP
    Go to the Automation Controller UI. Register a new execution environment using the pushed image.

### 4. Configure Variables
    Edit the file: group_vars/all/auth.yml 
    Update values according to your deployment.
    Some of the ways secrets can be passed using: Extra variables, Survey, Ansible Vault

### 5. Create a Source Control Credential
Create an SCM credential that has access to this repository.

### 6. Create a Project
Use the above SCM credential to link this Git repository to your AAP project.

### 7. Create an Inventory
    Create an inventory in AAP.Set its source to use inventory.yml in the root of this repo.

### 8. Create a Job Template
    Define a job template that uses: The inventory, The project, The execution environment, and The SCM credential
    Set the playbook to run: playbooks/aap_config.yml

### 9. Run the Job Template

Running this job template will apply the configuration and create AAP objects based on values defined under group_vars/all.
