data "aws_cloudfront_origin_request_policy" "managed_all_viewer_except_host_header" {
  name = "Managed-AllViewerExceptHostHeader"
}

data "aws_cloudfront_cache_policy" "managed_caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_iam_policy_document" "access_api_key_encryption_key" {
  statement {
    actions   = ["ssm:Get*"]
    resources = [aws_ssm_parameter.api_key_encryption_key.arn]
  }
}
