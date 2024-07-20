terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "random_id" "id" {
  byte_length = 4
}

locals {
  module_id                                       = coalesce(var.module_id, random_id.id.hex)
  viewer_request_interceptor_lambda_function_name = "viewer-request-interceptor-${local.module_id}"
}

resource "aws_ssm_parameter" "allowlisted_organizaion_ids" {
  name  = "us-east-1.${local.viewer_request_interceptor_lambda_function_name}-allowlisted_organizaion_ids"
  type  = "String"
  value = jsonencode(var.allowlisted_organizaion_ids)
}

module "viewer_request_interceptor_lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  lambda_at_edge = true
  function_name  = local.viewer_request_interceptor_lambda_function_name
  handler        = "index.lambda_handler"
  runtime        = "python3.12"

  source_path        = "../lambda-src/viewer-request-interceptor"
  policy_json        = <<-EOT
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:Get*"
                ],
                "Resource": ["${aws_ssm_parameter.allowlisted_organizaion_ids.arn}"]
            }
        ]
    }
  EOT
  attach_policy_json = true
}

resource "aws_cloudfront_distribution" "proxy_distribution" {
  origin {
    domain_name = "api.openai.com"
    origin_id   = "openai"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled         = true
  is_ipv6_enabled = true
  comment         = "OpenAI proxy ${local.module_id}"
  price_class     = "PriceClass_100" # Use only North America and Europe

  default_cache_behavior {
    target_origin_id       = "openai"
    viewer_protocol_policy = "https-only"

    allowed_methods = [
      "HEAD",
      "DELETE",
      "POST",
      "GET",
      "OPTIONS",
      "PUT",
      "PATCH"
    ]
    cached_methods           = ["GET", "HEAD"]
    compress                 = true
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.managed_all_viewer_except_host_header.id
    cache_policy_id          = data.aws_cloudfront_cache_policy.managed_caching_disabled.id

    lambda_function_association {
      event_type = "viewer-request"
      lambda_arn = module.viewer_request_interceptor_lambda_function.lambda_function_qualified_arn
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

output "proxy_distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.proxy_distribution.id
}

output "proxy_distribution_domain_name" {
  description = "the domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.proxy_distribution.domain_name
}
