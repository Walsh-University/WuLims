# OIDC Setup (Microsoft Entra or Authentik)

WuLims supports OpenID Connect (OIDC) login using `mozilla-django-oidc`.

## 1. Install dependency

```bash
uv sync
```

## 2. Enable OIDC in `.env`

```bash
OIDC_ENABLED=1
OIDC_PROVIDER_NAME=Microsoft Entra
OIDC_LOGIN_ONLY=0

OIDC_RP_CLIENT_ID=<client-id>
OIDC_RP_CLIENT_SECRET=<client-secret>
OIDC_RP_SIGN_ALGO=RS256
OIDC_RP_SCOPES=openid,email,profile

# Preferred: discovery endpoint
OIDC_OP_DISCOVERY_ENDPOINT=<issuer>/.well-known/openid-configuration

# Optional (only if not using discovery)
# OIDC_OP_AUTHORIZATION_ENDPOINT=
# OIDC_OP_TOKEN_ENDPOINT=
# OIDC_OP_USER_ENDPOINT=
# OIDC_OP_JWKS_ENDPOINT=
# OIDC_OP_LOGOUT_ENDPOINT=
```

## 3. Identity provider callback URL

Configure this redirect URI in your OIDC app registration:

```text
http://localhost:8000/oidc/callback/
```

For production, use your public host:

```text
https://<your-domain>/oidc/callback/
```

## 4. Provider examples

### Microsoft Entra ID

Typical discovery endpoint pattern:

```text
https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration
```

Notes:
- If your team says "login.microsoft.com", confirm the actual OIDC issuer and discovery URL from the app registration metadata.
- Include `openid profile email` scopes.

### Authentik

Typical issuer/discovery pattern:

```text
https://<authentik-host>/application/o/<slug>/
https://<authentik-host>/application/o/<slug>/.well-known/openid-configuration
```

Use the discovery URL from the Authentik provider UI for your specific application.

## 5. User mapping behavior in WuLims

On first successful login, WuLims creates a local `accounts.User` with:
- `external_id` from OIDC `sub`
- `email` from `email` (or `upn` fallback)
- `first_name` from `given_name`
- `last_name` from `family_name`
- `employee_id` from `employee_id` / `employeeId` when present
- `department` from `department` when present

On subsequent logins, these fields are updated from claims when values are present.

## 6. Login UX

- The existing `/accounts/login/` page shows a "Sign in with <provider>" button when `OIDC_ENABLED=1`.
- Set `OIDC_LOGIN_ONLY=1` to hide the username/password form and force SSO-first login UX.

## 7. Security and production notes

- Keep `OIDC_RP_CLIENT_SECRET` in environment variables or secret manager only.
- Keep `OIDC_VERIFY_SSL=1` except for temporary local lab testing.
- Ensure `DJANGO_PUBLIC_URL`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` match your deployed URL.
