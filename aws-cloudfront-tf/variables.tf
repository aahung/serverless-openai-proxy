variable "module_id" {
  default     = null
  description = "Module ID used as suffix to resource names. Leave blank to use a random string."
}

variable "allowlisted_organizaion_ids" {
  type        = list(string)
  default     = []
  description = "List of organization IDs that are allowed to access the proxy. Leave blank to allow any organizations."
}
