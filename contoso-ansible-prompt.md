# Contoso EC2 Ansible Deployment

_Reverse-engineered prompt — exported 2026-07-17_

Write an Ansible setup that provisions and configures an EC2 instance to run
this repo's FastAPI backend + React (Vite) frontend, with Postgres on RDS and
file storage on real S3 (no Docker, no MinIO on the instance).

## Provisioning (new EC2 instance + security group)

- Use `amazon.aws` from the control machine to create the instance — don't
  assume it already exists.
- Resolve the default VPC/subnet if none is given; look up the latest Ubuntu
  24.04 AMI from Canonical dynamically (no hardcoded AMI id — they go stale
  per region).
- Security group: SSH (22) restricted to a configurable admin CIDR (never
  `0.0.0.0/0`), HTTP (80) and HTTPS (443) open. Nothing else — the backend
  only listens on 127.0.0.1, behind Nginx.
- Launch with that SG, a gp3 root volume, and an existing key pair name
  (don't generate one — there's no safe way to hand the `.pem` back).
- Once SSH is up, idempotently append the public IP to the inventory's
  `[web]` group (update in place on rerun, never duplicate).
- Split vars: `[provisioners]` (localhost, AWS region/instance type/key
  name/admin CIDR) vs `[web]` (app config), so the two don't collide.

## Configuring the instance (backend + frontend + nginx)

- No Docker on the box: backend runs under systemd, frontend is built to
  static files served by Nginx.
- Backend: let `uv` manage the pinned Python version and `uv sync --locked`
  the project; run via `uv run uvicorn app.main:app` under systemd (multiple
  workers, `Restart=on-failure`, `NoNewPrivileges`/`ProtectSystem` hardening).
- Frontend: Node via NodeSource, `npm ci && npm run build` with the API base
  set to a relative `/api` — same-origin, no CORS, no domain hardcoded into
  the bundle.
- Nginx: SPA fallback (`try_files $uri /index.html`), reverse-proxy `/api/`
  to the backend stripping the prefix, with websocket Upgrade/Connection
  headers for a `/ws/...` chat endpoint under that same path.
- TLS is optional and self-bootstrapping via certbot's HTTP-01 webroot
  challenge: render the site config twice — challenge-only first, the 443
  block only once the cert exists — flushing handlers in between, so it
  never references a not-yet-existing cert file.
- Also lock down the host with ufw (22/80/443), on top of the cloud SG.

## Externalized services (not provisioned by this playbook)

- `DATABASE_URL` points at RDS Postgres — not created here.
- Storage is real S3, not MinIO: no endpoint override and no static keys —
  credentials come from the instance's IAM role (needs `s3:PutObject`/
  `GetObject` on the bucket).
- Secrets (DB creds, JWT key, any third-party API keys) live in an
  ansible-vault-encrypted vars file referenced by name from the plain vars
  file; ship a `.example` with placeholders and copy/fill/encrypt
  instructions.

## Structure

- Roles: `provision` (AWS API only), `common` (packages, app user, git
  checkout, firewall), `backend`, `frontend`, `nginx`.
- Two playbooks, run in order: `provision.yml` then `site.yml`.
- `requirements.yml` (`community.general`, `amazon.aws`) and
  `requirements.txt` (boto3/botocore — control node only, not the target).
- Validate with `ansible-playbook --syntax-check` on both, plus a throwaway
  local test for idempotency-sensitive modules like `blockinfile`.
