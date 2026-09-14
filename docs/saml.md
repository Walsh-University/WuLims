# SAML2 Setup (Microsoft Entra)

WuLims supports SAML2 login using `djangosaml2`, integrating with Microsoft Entra ID as a SAML Enterprise Application.

## 1. Install dependency

```bash
uv sync
```

`djangosaml2` shells out to the `xmlsec1` binary, which must be installed on the host/container (already added to `docker/Dockerfile` and `docker/Dockerfile_alpine`). For local dev:

```bash
# macOS
brew install libxmlsec1

# Debian/Ubuntu
sudo apt-get install xmlsec1
```

## 2. Generate an SP signing keypair

Generate this once per environment and keep the key out of version control:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout sp_private_key.pem -out sp_public_cert.pem \
  -days 3650 -subj "/CN=wulims-sp"
```

Point `SAML_SP_KEY_FILE`/`SAML_SP_CERT_FILE` at these files.

## 3. Enable SAML2 in `.env`

```bash
SAML_ENABLED=1
SAML_PROVIDER_NAME=Microsoft Entra
SAML_LOGIN_ONLY=0

SAML_SP_ENTITY_ID=https://<your-domain>/saml2/metadata/
SAML_ACS_URL=https://<your-domain>/saml2/acs/

SAML_IDP_METADATA_FILE=/path/to/entra_federation_metadata.xml
SAML_SP_KEY_FILE=/path/to/sp_private_key.pem
SAML_SP_CERT_FILE=/path/to/sp_public_cert.pem
SAML_XMLSEC_BINARY=/usr/bin/xmlsec1
```

## 4. Register the Enterprise Application in Entra

1. Entra admin center → **Enterprise applications** → **New application** → **Create your own application** → **Integrate any other application you don't find in the gallery (Non-gallery)**.
2. Open the app → **Single sign-on** → **SAML**.
3. **Basic SAML Configuration**:
   - Identifier (Entity ID): the value of `SAML_SP_ENTITY_ID`.
   - Reply URL (Assertion Consumer Service URL): the value of `SAML_ACS_URL`.
4. **Attributes & Claims** — configure these claims (edit the defaults so the names match exactly):
   - `http://schemas.microsoft.com/identity/claims/objectidentifier` → user's Object ID (usually present by default).
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` → `user.mail`.
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname` → `user.givenname`.
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname` → `user.surname`.
   - Add custom claims named exactly `employeeid` and `department` sourced from the corresponding Entra user attributes, if you want those synced.
5. **SAML Certificates** — download the **Federation Metadata XML** and save it to the path referenced by `SAML_IDP_METADATA_FILE`.
6. Assign users/groups to the Enterprise Application under **Users and groups**.

## 5. User mapping behavior in WuLims

On first successful login, WuLims creates a local `accounts.User`, matched in this order:
1. `external_id` matches the Entra Object ID claim.
2. Falls back to a case-insensitive match on `email`.
3. Otherwise creates a new user, with a collision-safe username derived from the email local-part (or the Object ID if no email claim is present).

On every login, `email`/`first_name`/`last_name`/`employee_id`/`department` are refreshed from the incoming claims whenever a claim value is present and differs from the stored value.

## 6. Login UX

- The `/accounts/login/` page shows a "Sign in with <provider>" button linking to `/saml2/login/` when `SAML_ENABLED=1`.
- Set `SAML_LOGIN_ONLY=1` to hide the username/password form and force SSO-first login UX.
- Logout still goes through WuLims' local Django logout view; it does not perform IdP-side Single Logout against Entra.

## 7. Security and production notes

- Keep `SAML_SP_KEY_FILE` outside version control and readable only by the app's runtime user.
- Re-download `SAML_IDP_METADATA_FILE` if Entra rotates its signing certificate (Entra warns ahead of expiry in the Enterprise Application overview).
- Ensure `DJANGO_PUBLIC_URL`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` match your deployed URL, since `SAML_SP_ENTITY_ID`/`SAML_ACS_URL` must be reachable at that host.
