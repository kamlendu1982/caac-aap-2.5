# Splunk Lab - Ansible Deployment

Idempotent Ansible role to deploy Splunk Enterprise via Docker on any Linux VM.

## Prerequisites

- Ansible 2.14+
- `community.docker` collection: `ansible-galaxy collection install community.docker`
- Target VM with SSH access

## Quick Start

1. Update `inventory/hosts.yml` with your VM IP and user.
2. Edit `group_vars/splunk_hosts/vars.yml` for your desired config.
3. Set secrets in `group_vars/splunk_hosts/vault.yml` and encrypt:
   ```
   ansible-vault encrypt group_vars/splunk_hosts/vault.yml
   ```
4. Run the playbook:
   ```
   ansible-playbook -i inventory/hosts.yml site.yml --ask-vault-pass
   ```

## Rebuild on New VM

Same command — fully idempotent:
```
ansible-playbook -i inventory/hosts.yml site.yml --ask-vault-pass
```

## AAP Integration

- Store vault password in AAP as a **Vault Credential**
- Point an AAP **Project** to this Git repo
- Create a **Job Template** using `site.yml`
- Optional: add a **Survey** for `splunk_version` to parameterize upgrades
