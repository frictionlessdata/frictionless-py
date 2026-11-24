# Security

Frictionless reads local files and downloads remote resources as instructed by the provided metadata (a resource `path`, a package `profile`, a remote reference `$ref` inside the profile, etc.). This page explains the risks and best practices to follow for untrusted metadata (e.g. for a validation API).

## Validating trusted vs untrusted input

In the context of **a local user validating their own trusted data**, the command line `frictionless validate --trusted` flag, or the [`system` context](./system.md#system-context) provides a way to disable overly cautious security checks.

In the context of **validation of untrusted input**, `trusted` must stay `False` (the default), and in case of a service, deployment measures described below are recommanded.

Note that the safety checks validate **descriptors** (the metadata provided as a dictionary, a file, or a URL). Values you pass yourself in the Python API, such as `Resource('/any/path.csv')`, are under your own responsibility.

## What the default mode protects

When `trusted` is `False` (the default), local disk access provided by the metadata must stay inside the working directory. For a resource, the `path`, `extrapaths`, `profile`, `dialect`, and `schema` properties must be relative paths, without `..`, `~`, or environment variables. The same rule applies to a package `profile`. A rejected path yields a `path "..." is not safe` error.

For a profile `"$ref"`, additional rules apply:

- a local `"$ref"` is only followed from a local profile, and only within the working directory;
- a `file://` URI is refused
- only `http(s)` and local `"$ref"`s are supported: other schemes, such as `data:` or `ftp:`, are refused.

When a profile `"$ref"` points to a non-existent JSON pointer or anchor, the error message names the pointer, but does not disclose the content of the referenced document: a `"$ref"` can target any file of the working directory, whose content may be confidential.

## What the default mode does not protect

- **The working directory is readable:** by design, Frictionless reads the files of the working directory: as data (validation errors display cell contents), as a profile, or as a local profile `"$ref"`. In presence of untrusted input, do not run the framework from a directory that contains secrets.
- **The network is reachable:** any remote URL provided by the metadata is downloaded by the process. This is the intended behavior for legitimate user, but for a service on a server validating untrusted descriptor, it can result in a Server Side Request Forgery (SSRF) vulnerability.A user can probe the server's internal network : error messages and the difference between a response, an error, and a timeout can reveal information about internal services. Private IP addresses are not filtered by default.
- **Symlinks:** the checks operate on the path, not its target: a symlink inside the working directory pointing outside is followed.

## Best practices for a validation service

- Run the workers in a **dedicated, empty working directory**
- Use `validate_descriptor`, which returns a report instead of raising, for predictable error handling:

```python tabs=Python
from frictionless import Package

report = Package.validate_descriptor(descriptor)
for error in report.errors:
    print(error.note)
```

- Remote metadata downloads use a **10 seconds timeout**, so an unresponsive server cannot block a validation indefinitely. To use a different timeout, inject a custom session that overrides it.
- Keep `trusted` at its default (`False`) for any user-provided input
- Protect the service against SSRF (see below)

### Protecting a service against SSRF

To protect against Server-Side Request Forgery, here are some suggestions :

1. **Filter the outgoing network traffic** at the infrastructure level: firewall, cloud security groups etc. Ideally, run the validation workers in a network segment without access to the internal network.
2. **Inject a hardened HTTP session.** The session provided through `system.use_context(http_session=...)` is used for every remote metadata download. Resolve and validate the IP **at the moment of connection**, not beforehand, to defeat DNS rebinding: a check done before the request is sent can be bypassed by a DNS response that flips between a public and a private address. Use the standard-library [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) module for the check; the [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) describes this pattern.
3. **If the acceptable remote resources are known**, restrict them to this set, for example with a session adapter that only allows a fixed list of hosts.

## Reference

```yaml reference
references:
  - frictionless.System
```
