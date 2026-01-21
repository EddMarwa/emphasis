# External Integration Tasks (To Be Completed Manually)

## Payments
- **M-Pesa Daraja**: Create app credentials (Consumer Key/Secret), set callback URLs (STK push, B2C), obtain shortcode/paybill, register URLs, and store them in environment variables. Update backend payment client with these keys and endpoints.
- **Crypto gateway (USDT/BTC, TRC20/ERC20)**: Choose provider (e.g., Coinbase Commerce or NOWPayments), generate API keys/webhook secrets, configure webhook endpoint URL, and map currency -> wallet routes. Store keys in environment variables.
- **Exchange rates**: Choose source (e.g., provider API or fixer.io), obtain API key, and schedule periodic rate pulls.

## Communications
- **Email**: Pick SMTP provider (SendGrid/Mailgun), create API key/domain, verify sender, and set env vars for SMTP host/user/password/from.
- **SMS**: Choose provider (Twilio/others), obtain SID/auth token/number or sender ID, and set env vars.

## File/Media Storage
- **S3/Cloudinary**: Create bucket/cloud name, API keys, configure upload presets/ACL, and set env vars.

## Security & Compliance
- **Production secrets**: Generate unique `SECRET_KEY`, JWT signing key (if distinct), and set `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `SECURE_SSL_REDIRECT` per environment.
- **Certificates**: Configure TLS certs/ACME for chosen domain(s).

## Banking/Finance Controls
- **Limits & rules**: Define minimum deposit, withdrawal limits, and KYC thresholds; encode them in backend settings or admin-configurable table.
- **Audit/receipts**: Decide receipt format (PDF/HTML), storage location, and signing/numbering scheme.

## Webhooks & Callbacks
- Expose reachable HTTPS endpoints for payment webhooks (M-Pesa confirmations, crypto gateway events) and record them with providers.

## Monitoring & Logging
- Choose error/uptime monitoring (Sentry/New Relic/Healthchecks), configure DSN/API keys, and set env vars.

> These items must be completed with provider portals and environment configuration before live funds or notifications can function.
