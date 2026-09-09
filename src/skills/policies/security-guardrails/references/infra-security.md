# Infrastructure Security Examples

These fragments are optional patterns for when the matching boundary already exists. They do not require a rotation service, TLS-only policy, Alpine base image, scanner, or CI workflow.

## Restricting Credential Files

When secrets are files, limit who can read them. This is not a 90-day rotation engine.

```bash
install -d -m 700 /etc/secrets
install -m 600 "$TMP_SECRET" /etc/secrets/db_password
```

## TLS When The Path Needs It

Use TLS for exposed HTTP when confidentiality or integrity matters. Do not require TLS 1.3-only, OCSP stapling, or HSTS preload.

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    ssl_certificate     /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
}
```

## Container Runtime Slice

Drop build tools from the runtime image and avoid root when the process allows it. Keep the image family the project already owns; no specific base image or scanner is required.

```dockerfile
# Runtime stage only: copy the built artifact, drop the toolchain, and run
# non-root when the process does not need root.
FROM runtime-base
COPY --from=build /out/app /usr/local/bin/app
USER 1001
ENTRYPOINT ["/usr/local/bin/app"]
```
