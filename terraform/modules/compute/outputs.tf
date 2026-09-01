output "instance_id"        { value = oci_core_instance.app_host.id }
output "public_ip"          { value = oci_core_instance.app_host.public_ip }
output "instance_state"     { value = oci_core_instance.app_host.state }