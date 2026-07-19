# SS1 Deployment & Operational Runbook

This runbook outlines the deployment, configuration, ownership/permissions, schema migration, and maintenance instructions for Project Mnemosyne and the Solomon API on SS1.

---

## 1. Prerequisites and Folder Structure

Deploying this architecture requires the following paths and configurations to be set up on SS1:

### Directories & File Ownership
- **Preferred Data Root:** `/srv/storage/toshiba/BubblePath/data/mnemosyne/`
- **Owner Linux User:** `millerm` (or the daemon user designated to run `solomon-api.service`)
- **Group:** `millerm`
- **Directory Permissions:** `750` (`drwxr-x---`)
- **SQLite Database File Permissions:** `640` (`-rw-r-----`)

Ensure the directories exist and are owned by the proper user:
```bash
sudo mkdir -p /srv/storage/toshiba/BubblePath/data/mnemosyne
sudo chown -R millerm:millerm /srv/storage/toshiba/BubblePath/data/mnemosyne
sudo chmod 750 /srv/storage/toshiba/BubblePath/data/mnemosyne
```

---

## 2. Configuration Deployment

The services load environmental values from a central configuration file.
1. Copy the template from `deploy/env/solomon.env.example` to `/etc/solomon/solomon.env`:
   ```bash
   sudo mkdir -p /etc/solomon
   sudo cp deploy/env/solomon.env.example /etc/solomon/solomon.env
   sudo chown millerm:millerm /etc/solomon/solomon.env
   sudo chmod 600 /etc/solomon/solomon.env
   ```
2. Open `/etc/solomon/solomon.env` and populate the actual secrets for:
   - `SOLOMON_ACTIONS_API_KEY` (Generate a random high-entropy token)
   - `OPENAI_API_KEY` (Production OpenAI key)

---

## 3. Systemd Services Installation

1. Install the Systemd service definition for the API:
   ```bash
   sudo cp deploy/systemd/solomon-api.service.example /etc/systemd/system/solomon-api.service
   sudo cp deploy/systemd/solomon-proxy.service.example /etc/systemd/system/solomon-proxy.service
   ```
2. Reload and enable systemd units:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable solomon-api.service
   sudo systemctl enable solomon-proxy.service
   ```

---

## 4. Run Automated Deployment

To safely pull, update dependencies, run tests, apply database migrations, and restart active units, run:
```bash
./deploy/scripts/deploy_ss1.sh
```

---

## 5. Rollback Procedures

If the readiness probe or health check fails after deployment, the deployment script executes rollback automatically.
To trigger a manual emergency rollback to the previous configuration and database snapshot:
```bash
./deploy/scripts/rollback_ss1.sh
```
