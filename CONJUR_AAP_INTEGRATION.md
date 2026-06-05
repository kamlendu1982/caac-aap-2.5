# Conjur OSS — AAP Integration Guide (Lab)

This document explains how to obtain the values needed for the **CyberArk Conjur Secrets Manager Lookup** credential in Ansible Automation Platform (AAP), after deploying Conjur with `playbooks/deploy_cyberArk_conjur.yml`.

> **Lab only.** The HTTP URL below is acceptable inside a private VPC. Do not use this setup for production.

---

## Quick reference (same VPC lab)

| AAP credential field | Typical lab value | Where to get it |
|----------------------|-------------------|-----------------|
| **Conjur URL** | `http://<conjur-private-ip>:8080` | Conjur VM private IP (see below) |
| **Account** | `myConjurAccount` | Playbook extra var `conjur_account` (default) |
| **Username** | `admin` | Built-in Conjur admin user |
| **API Key** | long alphanumeric string | `/opt/conjur/admin_data` on Conjur VM |
| **Public Key Certificate** | *(leave blank for HTTP lab)* | `/opt/conjur/conf/tls/nginx.crt` (HTTPS only) |
| **Test Secret Identifier** | `db_password` | Default lab secret from playbook |

---

## 1. Deploy Conjur

**Option A — Ansible CLI:**

```bash
ansible-playbook playbooks/deploy_cyberArk_conjur.yml -i inventory.yml \
  -e "conjur_account=myConjurAccount conjur_admin_pass='MySecretP@SS1'"
```

**Option B — AAP job template (after CaaC apply):**

1. Run `controller_config` (or your CaaC job) to sync objects from this repo.
2. Update `inventory.yml` with the Conjur EC2 host under `conjur_host`.
3. Sync the `conjur_host` inventory in AAP.
4. Run job template **Deploy CyberArk Conjur OSS**.
5. Read AAP integration values from the **job output** or `/opt/conjur/AAP_INTEGRATION.txt` on the Conjur VM.

By default the playbook also:

- Creates admin account and saves credentials to `/opt/conjur/admin_data`
- Loads a lab secret variable `db_password` (for AAP testing)
- Enables `conjur-containers.service` so containers restart after EC2 reboot

---

## 2. Get integration values on the Conjur VM

SSH to the Conjur host and run:

```bash
cd /opt/conjur

# Private IP — use this for Conjur URL when AAP is in the same VPC
hostname -I | awk '{print $1}'

# Account name
grep -i "Created new account" admin_data 2>/dev/null | awk '{print $NF}' || echo "myConjurAccount"

# Admin API key (for AAP "API Key" field)
grep "Admin API Key:" admin_data | sed 's/^Admin API Key: //'

# If API key line is missing, retrieve it:
podman exec conjur_server conjurctl role retrieve-key myConjurAccount:user:admin | tail -1

# TLS certificate (only if using HTTPS :8443)
cat conf/tls/nginx.crt

# Verify Conjur is up
curl -s -w "\nHTTP: %{http_code}\n" http://127.0.0.1:8080
podman ps --format "table {{.Names}}\t{{.Status}}"
```

### Example output mapping

If private IP is `10.0.1.218`:

```
Conjur URL : http://10.0.1.218:8080
Account    : myConjurAccount
Username   : admin
API Key    : 1c2mjh41wv6nxb1bnp5ykda3ah52cnyd283ssjyt1gx062r85d25
Certificate: (blank for HTTP lab)
```

---

## 3. Verify connectivity from the AAP VM

On the AAP controller (or execution node that resolves credentials):

```bash
CONJUR_URL="http://10.0.1.218:8080"   # replace with your Conjur private IP
curl -sk -w "\nHTTP: %{http_code}\n" "${CONJUR_URL}/health"
```

Expected: `Authorization missing` with **HTTP 401** (Conjur is reachable).

Full auth + secret test:

```bash
CONJUR_URL="http://10.0.1.218:8080"
ACCOUNT="myConjurAccount"
USER="admin"
API_KEY="<paste-admin-api-key>"

TOKEN=$(curl -s -d "$API_KEY" "$CONJUR_URL/authn/$ACCOUNT/$USER/authenticate")
curl -s -H "Authorization: Token token=\"${TOKEN}\"" \
  "$CONJUR_URL/secrets/$ACCOUNT/variable/db_password"
echo
```

Expected: `SuperSecret123!` (or your configured secret value).

---

## 4. Create credentials in AAP

### Step A — Conjur lookup credential

1. **Resources → Credentials → Add**
2. **Credential type:** CyberArk Conjur Secrets Manager Lookup
3. Fill in:

| Field | Value |
|-------|--------|
| Name | `Conjur OSS Lab` |
| Conjur URL | `http://10.0.1.218:8080` |
| Account | `myConjurAccount` |
| Username | `admin` |
| API Key | *(from admin_data)* |
| Public Key Certificate | *(leave blank for HTTP lab)* |

4. Click **Test** and enter:
   - **Secret Identifier:** `db_password`
   - **Secret Version:** *(blank)*

### Step B — Credential that consumes the secret

1. Create a **Machine** (or other) credential
2. Set **External Secret Management System** to `Conjur OSS Lab`
3. **Secret Identifier:** `db_password`
4. Attach to a job template

---

## 5. Network / security group

When AAP and Conjur are in the **same VPC**, allow:

| Direction | Port | Purpose |
|-----------|------|---------|
| AAP → Conjur | **8080** | HTTP API (lab — credential test passed) |
| AAP → Conjur | **8443** | HTTPS via nginx (optional) |

Use the Conjur **private IP** (`10.x.x.x`), not the internal DNS name, unless your VPC resolves it.

---

## 6. HTTPS (optional)

If you prefer `https://<ip>:8443`:

1. Paste the full contents of `/opt/conjur/conf/tls/nginx.crt` into **Public Key Certificate**
2. Ensure no extra spaces or missing `BEGIN/END` lines
3. Allow port **8443** in the security group

In our lab, AAP credential test passed with **HTTP :8080** and blank certificate.

---

## 7. After EC2 stop/start

Containers do not auto-start unless systemd is enabled (playbook default):

```bash
sudo systemctl status conjur-containers.service
sudo systemctl start conjur-containers.service   # if needed
```

Or re-run the deploy playbook (idempotent).

---

## 8. Useful CLI commands (on Conjur VM)

```bash
# Log in
API_KEY=$(grep "Admin API Key:" /opt/conjur/admin_data | sed 's/^Admin API Key: //')
podman exec conjur_client conjur login -i admin -p "$API_KEY"

# Read / update secret
podman exec conjur_client conjur variable get -i db_password
podman exec conjur_client conjur variable set -i db_password -v 'NewValue456!'

# Log out
podman exec conjur_client conjur logout
```

---

## 9. Files to protect

| File | Contents |
|------|----------|
| `/opt/conjur/admin_data` | Account info + admin API key |
| `/opt/conjur/data_key` | Conjur master encryption key |

Do not commit these files to git.

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| AAP test **Bad Request** with HTTPS | Use `http://<private-ip>:8080` and blank certificate (lab) |
| **Unable to authenticate** in CLI | Reset client config: `podman exec conjur_client rm -f /home/cli/.conjurrc` then re-run `conjur init` |
| Containers down after reboot | `sudo systemctl start conjur-containers.service` |
| API key unknown | `podman exec conjur_server conjurctl role retrieve-key myConjurAccount:user:admin \| tail -1` |
| Policy load fails for nested `myapp/` | Use flat root policy (see playbook `aap-lab-secret.yml`) |

---

## Related files

- Deploy playbook: `playbooks/deploy_cyberArk_conjur.yml`
- AAP job template: `Deploy CyberArk Conjur OSS` in `group_vars/all/job_templates.yml`
- Inventory: `inventory.yml` (`conjur_host` group)
- Post-deploy summary on VM: `/opt/conjur/AAP_INTEGRATION.txt`
- Upstream quickstart: https://github.com/kamlendu1982/conjur-quickstart
