variable "aws_region" {
  description = "AWS region"
  type        = "string"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = "string"
  default     = "creatoriq"
}

variable "db_password" {
  description = "Database password"
  type        = "string"
  sensitive   = true
}
