variable "os_cloud" {
  description = "OpenStack cloud profile name from clouds.yaml."
  type        = string
  default     = "myopenstack"
}

variable "image_name" {
  description = "OpenStack image name for the virtual machine."
  type        = string
}

variable "flavor_name" {
  description = "OpenStack flavor name for the virtual machine."
  type        = string
}

variable "flavor_id" {
  description = "Optional OpenStack flavor ID. Use it when provider flavor lookup by name is slow or unavailable."
  type        = string
  default     = ""
}

variable "external_network_name" {
  description = "External OpenStack network name for router gateway and floating IP."
  type        = string
}

variable "public_key_path" {
  description = "Path to the public SSH key used to create the OpenStack keypair."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "keypair_name" {
  description = "Name of the SSH keypair created in OpenStack."
  type        = string
  default     = "greenhouse-monitor-key"
}

variable "docker_image" {
  description = "Docker image that cloud-init will run on the virtual machine."
  type        = string
}

variable "ssh_cidr" {
  description = "CIDR allowed to connect to the virtual machine over SSH."
  type        = string
  default     = "0.0.0.0/0"
}

variable "app_cidr" {
  description = "CIDR allowed to connect to the FastAPI application."
  type        = string
  default     = "0.0.0.0/0"
}

variable "subnet_cidr" {
  description = "CIDR for the private OpenStack subnet."
  type        = string
  default     = "10.10.0.0/24"
}

variable "dns_nameservers" {
  description = "DNS servers for instances in the private subnet."
  type        = list(string)
  default     = ["1.1.1.1", "8.8.8.8"]
}

