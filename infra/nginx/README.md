# Nginx

این پوشه شامل الگوی واقعی TLS reverse proxy برای API است:

- `farmnet.conf`: انتقال اجباری HTTP به HTTPS، TLS 1.2/1.3، HSTS،
  security headers و rate limit لبه؛
- `farmnet-proxy.conf`: هدرهای proxy، timeoutها و زنجیره‌ی
  `X-Forwarded-For`.

قبل از استقرار، دامنه و مسیر گواهی‌ها را با مقادیر واقعی عوض کنید. آدرس یا
CIDR شبکه‌ی Nginx باید در `TRUSTED_PROXY_HOSTS` Backend قرار گیرد و
`RATE_LIMIT_BACKEND=redis` باشد. این فایل به‌تنهایی deployment production
ایجاد نمی‌کند؛ topology، secrets و certificate automation در گام استقرار
تکمیل می‌شوند.
