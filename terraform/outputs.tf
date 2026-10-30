output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "app_url" {
  description = "Open this in your browser (wait 2-3 minutes after apply for Docker to start)"
  value       = "http://${aws_instance.app.public_ip}"
}

output "ssh_command" {
  description = "Command to connect to the instance"
  value       = "ssh -i ${var.key_name}.pem ec2-user@${aws_instance.app.public_ip}"
}
