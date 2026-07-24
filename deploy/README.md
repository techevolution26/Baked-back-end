# Deploy: reverse proxy for domain-per-bakery

This is the production piece that makes "each bakery owns a unique
domain" actually work without manually issuing a TLS certificate for
every bakery that signs up.

## How it fits together

```
customer's browser
      |  (any bakery's domain, e.g. sweetfigbakery.com)
      v
   Caddy (:443, on-demand TLS)
      |  asks backend:8000/internal/domain-check first time it sees a domain
      |  reverse_proxy frontend:3000
      v
Next.js frontend
      |  middleware.ts reads the real Host header, forwards it to
      |  Server Components / API routes as X-Tenant-Host
      v
FastAPI backend (never exposed publicly, only reachable inside the
docker network by the frontend and by Caddy's "ask" check)
```

## Why on-demand TLS
A fixed list of domains in a static Caddyfile doesn't work here --
bakeries can add a custom domain at any time, and we don't want to
redeploy the proxy every time one does. Caddy's `on_demand_tls` instead
asks `GET /internal/domain-check?domain=<host>` before issuing a cert
for a hostname it hasn't seen before. Our backend answers based on
whether that hostname matches a bakery's `custom_domain` or
`<subdomain>.<PLATFORM_DOMAIN>`. If it 404s, Caddy refuses to issue a
certificate for it -- this is the guard that stops random domains from
being pointed at your infrastructure and getting a cert issued in your
name.

## Wiring this in
This isn't wired into `docker-compose.yml` yet because the frontend
isn't containerized yet (see the frontend repo's README). Once it is,
add a `frontend` service building the Next.js app, then add:

```yaml
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    depends_on:
      - frontend
      - backend

volumes:
  caddy_data:
```

`backend` must **not** publish port 8000 to the host in production --
only `caddy` and `frontend` should be reachable from outside the docker
network. The `/internal/domain-check` endpoint has no auth of its own;
its safety comes entirely from never being reachable except by Caddy
over the private network.

## DNS, in brief
- Platform subdomains: one wildcard DNS record, `*.cakeplatform.com A <server IP>`
- Custom domains: each bakery points their domain's A record at `<server IP>`
  (verification that they actually own it, before you'll show it as
  "verified" in the dashboard, isn't built yet -- flagged as a gap)
