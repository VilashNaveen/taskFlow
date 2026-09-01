module "network" {
  source           = "../../modules/network"
  compartment_ocid = var.compartment_ocid
  project_name     = "taskflow"
}

module "compute" {
  source              = "../../modules/compute"
  compartment_ocid    = var.compartment_ocid
  project_name        = "taskflow"
  subnet_id           = module.network.public_subnet_id
  ssh_public_key_path = "C:/Users/vilash/.ssh/taskflow_key.pub"
}

output "app_host_public_ip" {
  value = module.compute.public_ip
}