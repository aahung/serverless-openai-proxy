# Serverless OpenAI Proxy with AWS CloudFront and terraform

Commands:

```sh
tofu init
tofu plan
tofu apply
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 5.59.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.6.2 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_origin_request_interceptor_lambda_function"></a> [origin\_request\_interceptor\_lambda\_function](#module\_origin\_request\_interceptor\_lambda\_function) | terraform-aws-modules/lambda/aws | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_cloudfront_distribution.proxy_distribution](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_distribution) | resource |
| [aws_ssm_parameter.api_key_encryption_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [random_bytes.api_key_encryption_key](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/bytes) | resource |
| [random_id.id](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [aws_cloudfront_cache_policy.managed_caching_disabled](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/cloudfront_cache_policy) | data source |
| [aws_cloudfront_origin_request_policy.managed_all_viewer_except_host_header](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/cloudfront_origin_request_policy) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowlisted_organizaion_ids"></a> [allowlisted\_organizaion\_ids](#input\_allowlisted\_organizaion\_ids) | List of organization IDs that are allowed to access the proxy. Leave blank to allow any organizations. | `list(string)` | `[]` | no |
| <a name="input_enable_api_key_encryption"></a> [enable\_api\_key\_encryption](#input\_enable\_api\_key\_encryption) | Whether enable API key encryption. It's useful when you only want the API key to work via proxy. | `bool` | `false` | no |
| <a name="input_module_id"></a> [module\_id](#input\_module\_id) | Module ID used as suffix to resource names. Leave blank to use a random string. | `any` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_proxy_distribution_domain_name"></a> [proxy\_distribution\_domain\_name](#output\_proxy\_distribution\_domain\_name) | the domain name of the CloudFront distribution |
| <a name="output_proxy_distribution_id"></a> [proxy\_distribution\_id](#output\_proxy\_distribution\_id) | The ID of the CloudFront distribution |
<!-- END_TF_DOCS -->