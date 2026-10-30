# Latest Amazon Linux 2023 image (x86_64, matches t3.micro and our amd64 Docker images)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
}

# Use the default VPC that every AWS account already has (no NAT gateway, no extra cost)
data "aws_vpc" "default" {
  default = true
}

# Firewall: SSH only from your IP, HTTP from anywhere. Port 8000 stays closed.
resource "aws_security_group" "app" {
  name        = "churn-terraform-sg"
  description = "Churn prediction app: HTTP from anywhere, SSH from my IP"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from my IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    description = "HTTP for the web app"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound (needed to pull Docker images)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true

  # Startup script: installs Docker and starts the app containers
  user_data = templatefile("${path.module}/user_data.sh", {
    dockerhub_username = var.dockerhub_username
    image_tag          = var.image_tag
  })

  root_block_device {
    volume_size = 8 # GB, within the Free Tier storage allowance
    volume_type = "gp3"
  }

  tags = {
    Name = "churn-terraform"
  }
}
