output "public_ip" {
  description = "Floating IP assigned to the virtual machine."
  value       = openstack_networking_floatingip_v2.vm.address
}

output "service_url" {
  description = "FastAPI service URL."
  value       = "http://${openstack_networking_floatingip_v2.vm.address}:8000"
}

output "health_url" {
  description = "FastAPI health check URL."
  value       = "http://${openstack_networking_floatingip_v2.vm.address}:8000/health"
}

output "optimal_greenhouses_url" {
  description = "Optimal greenhouse conditions URL."
  value       = "http://${openstack_networking_floatingip_v2.vm.address}:8000/optimal-greenhouses"
}

output "ssh_command" {
  description = "SSH command for the virtual machine."
  value       = "ssh ubuntu@${openstack_networking_floatingip_v2.vm.address}"
}

