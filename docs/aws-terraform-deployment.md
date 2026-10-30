# Terraform AWS Deployment — Step by Step

Terraform creates the same single-EC2 setup as the manual guide: one `t3.micro` instance and one security group.
On first boot, `user_data.sh` installs Docker, writes `docker-compose.yml` and starts the Docker Hub images by itself.

Commands are for Windows PowerShell, run from the `terraform/` folder.

## 1. Install tools (once)

```powershell
winget install Hashicorp.Terraform
winget install Amazon.AWSCLI
```

Restart PowerShell. If `terraform` is still not recognized:

```powershell
$env:Path += ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"
```

## 2. Log in to AWS

```powershell
aws login --region <REGION>
aws configure export-credentials --format powershell | Invoke-Expression
aws sts get-caller-identity
```

You also need an EC2 key pair (for example `churn-key`) in the same region.

## 3. Set your values

```powershell
copy terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars
```

Fill in `aws_region`, `key_name`, `my_ip_cidr` (your IP from https://checkip.amazonaws.com plus `/32`) and `dockerhub_username`.
`terraform.tfvars` is git-ignored.

## 4. Init, check and preview

```powershell
terraform init
terraform fmt
terraform validate
terraform plan -out=tfplan      # expect: Plan: 2 to add, 0 to change, 0 to destroy
```

## 5. Create the server

```powershell
terraform apply tfplan
terraform output                # public_ip, app_url, ssh_command
```

## 6. Test (wait 2–3 minutes for Docker to start)

```powershell
curl.exe http://<EC2_PUBLIC_IP>/api/health
# {"status":"ok","model_loaded":true}
```

Open `http://<EC2_PUBLIC_IP>` in the browser and run a prediction.
To look inside the server: `ssh -i <KEY_FILE> ec2-user@<EC2_PUBLIC_IP>` then `docker ps`.

## 7. Destroy (always, after testing)

```powershell
terraform destroy               # type yes → Destroy complete! Resources: 2 destroyed.
```

Optionally delete the key pair: `aws ec2 delete-key-pair --key-name <KEY_NAME> --region <REGION>`.
