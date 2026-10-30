variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type. Check it is marked Free Tier eligible for your account and region."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of an existing EC2 key pair, used for SSH access"
  type        = string
}

variable "my_ip_cidr" {
  description = "Your public IP in CIDR form (e.g. 203.0.113.10/32). Only this IP can SSH in."
  type        = string
}

variable "dockerhub_username" {
  description = "Docker Hub account that holds the churn-backend and churn-frontend images"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "v1.0.0"
}
