provider "openstack" {
  cloud = var.os_cloud
}

data "openstack_images_image_v2" "ubuntu" {
  name        = var.image_name
  most_recent = true
}

data "openstack_compute_flavor_v2" "vm" {
  count = var.flavor_id == "" ? 1 : 0
  name  = var.flavor_name
}

data "openstack_networking_network_v2" "external" {
  name = var.external_network_name
}

resource "openstack_networking_network_v2" "private" {
  name           = "greenhouse-monitor-network"
  admin_state_up = true
}

resource "openstack_networking_subnet_v2" "private" {
  name            = "greenhouse-monitor-subnet"
  network_id      = openstack_networking_network_v2.private.id
  cidr            = var.subnet_cidr
  ip_version      = 4
  dns_nameservers = var.dns_nameservers
}

resource "openstack_networking_router_v2" "router" {
  name                = "greenhouse-monitor-router"
  admin_state_up      = true
  external_network_id = data.openstack_networking_network_v2.external.id
}

resource "openstack_networking_router_interface_v2" "private" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.private.id
}

resource "openstack_networking_secgroup_v2" "app" {
  name        = "greenhouse-monitor-sg"
  description = "Security group for the smart greenhouse FastAPI service"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = var.ssh_cidr
  security_group_id = openstack_networking_secgroup_v2.app.id
}

resource "openstack_networking_secgroup_rule_v2" "app_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_ip_prefix  = var.app_cidr
  security_group_id = openstack_networking_secgroup_v2.app.id
}

resource "openstack_compute_keypair_v2" "app" {
  name       = var.keypair_name
  public_key = file(pathexpand(var.public_key_path))
}

resource "openstack_networking_port_v2" "vm" {
  name               = "greenhouse-monitor-port"
  network_id         = openstack_networking_network_v2.private.id
  admin_state_up     = true
  security_group_ids = [openstack_networking_secgroup_v2.app.id]

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.private.id
  }
}

resource "openstack_networking_floatingip_v2" "vm" {
  pool = data.openstack_networking_network_v2.external.name
}

resource "openstack_networking_floatingip_associate_v2" "vm" {
  floating_ip = openstack_networking_floatingip_v2.vm.address
  port_id     = openstack_networking_port_v2.vm.id

  depends_on = [
    openstack_compute_instance_v2.vm,
  ]
}

resource "openstack_compute_instance_v2" "vm" {
  name      = "greenhouse-monitor-vm"
  image_id  = data.openstack_images_image_v2.ubuntu.id
  flavor_id = var.flavor_id != "" ? var.flavor_id : data.openstack_compute_flavor_v2.vm[0].id
  key_pair  = openstack_compute_keypair_v2.app.name
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    docker_image = var.docker_image
  })

  network {
    port = openstack_networking_port_v2.vm.id
  }

  depends_on = [
    openstack_networking_router_interface_v2.private,
  ]
}

