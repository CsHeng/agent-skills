# Infrastructure Security Examples

Read this when the service exposes TLS, CORS, or response headers, handles credential files, or builds images. These fragments are optional patterns for a boundary the project already has; copy only what that boundary needs.

## Restricting Credential Files

When secrets are files, limit who can read them.

```bash
install -d -m 700 /etc/secrets
install -m 600 "$TMP_SECRET" /etc/secrets/db_password
```

## TLS When The Path Needs It

Use TLS for exposed HTTP when confidentiality or integrity matters. Choose protocol versions and ciphers the clients and threat model support.

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    ssl_certificate     /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
}
```

## Security Headers

Set the headers the application and its browser threat model need, such as frame isolation, content-type sniffing protection, referrer policy, or CSP.

## CORS

When the browser origin policy matters, allow the specific origins, methods, and headers the product requires.

## Container Runtime Slice

Drop build tools from the runtime image, run as non-root when the process allows it, and limit filesystem permissions to what the process needs. Keep the image family and CI the project already owns.

```dockerfile
# Runtime stage only: copy the built artifact, drop the toolchain, and run
# non-root when the process does not need root.
FROM runtime-base
COPY --from=build /out/app /usr/local/bin/app
USER 1001
ENTRYPOINT ["/usr/local/bin/app"]
```
