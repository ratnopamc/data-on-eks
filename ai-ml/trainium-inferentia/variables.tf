variable "name" {
  description = "Name of the VPC and EKS Cluster"
  default     = "trainium-inferentia-sd"
  type        = string
}

# NOTE: Trainium and Inferentia are only available in us-west-2 and us-east-1 regions
variable "region" {
  description = "region"
  default     = "us-west-2"
  type        = string
}

variable "eks_cluster_version" {
  description = "EKS Cluster version"
  default     = "1.28"
  type        = string
}

# VPC with 2046 IPs (10.1.0.0/21) and 2 AZs
variable "vpc_cidr" {
  description = "VPC CIDR. This should be a valid private (RFC 1918) CIDR range"
  default     = "10.1.0.0/21"
  type        = string
}

# RFC6598 range 100.64.0.0/10
# Note you can only /16 range to VPC. You can add multiples of /16 if required
variable "secondary_cidr_blocks" {
  description = "Secondary CIDR blocks to be attached to VPC"
  default     = ["100.64.0.0/16"]
  type        = list(string)
}

variable "enable_amazon_prometheus" {
  description = "Enable AWS Managed Prometheus service"
  type        = bool
  default     = true
}

variable "mpi_operator_version" {
  description = "The version of the MPI Operator to install"
  default     = "v0.4.0"
  type        = string
}

variable "enable_mpi_operator" {
  description = "Flag to enable the MPI Operator deployment"
  type        = bool
  default     = false
}

variable "inf2_8xl_min_size" {
  description = "Inf2-xl Worker node minimum size"
  type = number
  default = 0
}

variable "inf2_8xl_desired_size" {
  description = "Inf2-xl Worker node desired size"
  type = number
  default = 0 // adjust for your testing needs
}

variable "inf2_8xl_max_size" {
  description = "Inf2-xl Worker node maximum size"
  type = number
  default = 2
}

variable "inf2_capacity_type" {
  description = "Inf2 Worker node capacity type"
  type = string
  default = "ON_DEMAND" // change to "SPOT" after testing
}

variable "inf2_24xl_min_size" {
  description = "Inf2-24xl Worker node minimum size"
  type = number
  default = 0
}

variable "inf2_24xl_desired_size" {
  description = "Inf2-24xl Worker node desired size"
  type = number
  default = 1 // adjust for your testing needs
}

variable "inf2_24xl_max_size" {
  description = "Inf2-24xl Worker node maximum size"
  type = number
  default = 2
}