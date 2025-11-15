# ########################################
# Cloudflare
# ########################################
resource "cloudflare_record" "dns_record" {
  zone_id = var.cloudflare_zone_id
  name    = "${var.project}.${var.dns_domain}"
  content = aws_cloudfront_distribution.ecs_cdn.domain_name
  # content = aws_alb.lb.dns_name
  type    = "CNAME"
  ttl     = 1
  proxied = true
}

output "dns_url" {
  value = "https://${cloudflare_record.dns_record.hostname}"
}
