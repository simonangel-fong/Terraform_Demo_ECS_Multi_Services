data "aws_region" "current" {}

# acm certificate
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1" # Required for CloudFront ACM
}

data "aws_acm_certificate" "cf_certificate" {
  domain      = "*.${var.dns_domain}"
  provider    = aws.us_east_1
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

# ###############################
# CloudFront
# ###############################
resource "aws_cloudfront_distribution" "ecs_cdn" {

  origin {
    origin_id   = "${var.project}-cdn-origin"
    domain_name = aws_alb.lb.dns_name

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only" # S3 website endpoint supports HTTP only
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # default cache
  default_cache_behavior {
    target_origin_id       = "${var.project}-cdn-origin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    compress               = true

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  enabled     = true
  aliases     = ["${var.project}.${var.dns_domain}"]
  price_class = "PriceClass_100"

  viewer_certificate {
    acm_certificate_arn      = data.aws_acm_certificate.cf_certificate.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name = "${var.project}-cloudfront"
  }
}

output "cdn_domain" {
  value = aws_cloudfront_distribution.ecs_cdn.domain_name
}
