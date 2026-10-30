# Manual AWS EC2 Deployment — Step by Step

This guide deploys the app on **one EC2 instance** using the AWS Console and Docker Compose.
The Docker images are pulled from Docker Hub, so nothing is built on the server.

Replace these placeholders with your own values:

| Placeholder | Example |
|---|---|
| `<EC2_PUBLIC_IP>` | `13.51.178.19` |
| `<DOCKERHUB_USERNAME>` | `ubaidur404786` |
| `<KEY_FILE>` | `C:\Users\you\.ssh\churn-key.pem` |

---

## 1. Before you start (cost safety)

- Use an account on the AWS **Free plan** and never click **Upgrade plan**.
- Billing → **Budgets** → create a **Zero spend budget** with email alerts.
- Stay in one region (this project used `eu-north-1`, Stockholm).

## 2. Launch the EC2 instance (AWS Console)

EC2 → **Launch instance**:

| Setting | Value |
|---|---|
| Name | `churn-manual` |
| AMI | Amazon Linux 2023 (Free tier eligible) |
| Instance type | `t3.micro` (Free tier eligible) |
| Key pair | Create new → `churn-key`, RSA, `.pem` (keep it outside the repo) |
| Network | Allow SSH from **My IP**, allow **HTTP** from the internet |
| Storage | 8 GiB gp3 |

Click **Launch instance**, wait for **Running** and **2/2 checks passed**, then copy the **Public IPv4 address**.

## 3. Connect with SSH (Windows PowerShell)

Lock the key file once (SSH refuses keys that other users can read):

```powershell
icacls <KEY_FILE> /inheritance:r /grant:r "$($env:USERNAME):R"
```

Connect:

```powershell
ssh -i <KEY_FILE> ec2-user@<EC2_PUBLIC_IP>
```

On Linux/macOS use `chmod 400 churn-key.pem` instead of `icacls`.

## 4. Install Docker and Docker Compose (on the server)

```bash
# Install Docker, start it now and on every boot, allow ec2-user to use it
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Install the Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -fsSL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Log out and back in so the docker group permission applies
exit
```

Reconnect with the `ssh` command from step 3, then check:

```bash
docker --version
docker compose version
```

## 5. Create the compose file (on the server)

```bash
mkdir -p ~/churn-app && cd ~/churn-app

cat > docker-compose.yml <<'EOF'
services:
  backend:
    image: <DOCKERHUB_USERNAME>/churn-backend:v1.0.0
    restart: unless-stopped
  frontend:
    image: <DOCKERHUB_USERNAME>/churn-frontend:v1.0.0
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
EOF
```

## 6. Pull the images and start the app

```bash
docker compose pull      # download images from Docker Hub
docker compose up -d     # start both containers in the background
docker compose ps        # backend should be "healthy", frontend "Up"
curl http://localhost/api/health
```

Expected: `{"status":"ok","model_loaded":true}`

## 7. Test from your own computer

- Website: `http://<EC2_PUBLIC_IP>`
- Health check: `http://<EC2_PUBLIC_IP>/api/health`
- Prediction:

```bash
curl -X POST http://<EC2_PUBLIC_IP>/api/predict -H "Content-Type: application/json" -d '{"gender":"Female","SeniorCitizen":0,"Partner":"No","Dependents":"No","tenure":2,"PhoneService":"Yes","MultipleLines":"No","InternetService":"Fiber optic","OnlineSecurity":"No","OnlineBackup":"No","DeviceProtection":"No","TechSupport":"No","StreamingTV":"Yes","StreamingMovies":"Yes","Contract":"Month-to-month","PaperlessBilling":"Yes","PaymentMethod":"Electronic check","MonthlyCharges":95.5,"TotalCharges":190}'
```

Port 8000 is intentionally closed; the backend is only reachable through nginx on port 80.

## 8. Useful commands on the server

```bash
docker compose logs -f backend   # follow backend logs
docker compose restart           # restart both containers
docker compose down              # stop and remove the containers
```

## 9. Cleanup (do this when you finish testing)

On the server (optional, the instance is deleted next anyway):

```bash
cd ~/churn-app && docker compose down
exit
```

In the AWS Console:

1. EC2 → **Instances** → select `churn-manual` → **Instance state** → **Terminate (delete) instance** → confirm.
   This also deletes the 8 GiB disk and releases the public IP.
2. EC2 → **Security Groups** → select `launch-wizard-1` → **Actions** → **Delete security groups**
   (possible only after the instance is terminated).
3. EC2 → **Key Pairs** → select `churn-key` → **Actions** → **Delete** (and delete the local `.pem` if you no longer need it).
4. Check **EC2 → Elastic IPs** and **Volumes** are empty, and **Billing → Bills** shows no unexpected services.

Or with the AWS CLI (if configured):

```bash
aws ec2 terminate-instances --instance-ids <INSTANCE_ID> --region eu-north-1
aws ec2 wait instance-terminated --instance-ids <INSTANCE_ID> --region eu-north-1
aws ec2 delete-security-group --group-name launch-wizard-1 --region eu-north-1
aws ec2 delete-key-pair --key-name churn-key --region eu-north-1
```

> **Stop vs terminate:** *Stop* pauses the instance (disk is still stored, and a new public IP is assigned on restart).
> *Terminate* deletes everything. For a test deployment, terminate.
