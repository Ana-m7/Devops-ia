# Buildah vs Docker: Results

#### Timing & Size Comparison
| Aspect | Buildah | Docker |
|---|---|---|
| Build time (cold/warm) | 27.020s / 5.085s | 16.882s / 0.826s |
| Image size | 137 MB | 235 MB |
| Build flexibility | Containerfile or scripted steps | Dockerfile |
| Ease of use | more concepts to learn | simpler, more tutorials |
| CI/CD and Kubernetes fit | strong (no privileged daemon) | good, but needs Docker socket or DinD |

#### Architecture & Security Comparison
| Aspect | Buildah | Docker |
|---|---|---|
| Architecture | Daemonless | Client plus root daemon |
| Root required | No (rootless by default) | Daemon runs as root |

## Notes from Person 1
- `buildah build` does not cache layers unless `--layers` is passed.
- The step-by-step build (`buildah from/run/copy/commit`) produced an identical 137 MB image.
- WSL2 shows a harmless "/ is not a shared mount" warning under rootless Podman.
- Flask ignores SIGTERM as PID 1, so `podman stop` waits 10s before SIGKILL.
- DNS timeouts on the college network delayed the WSL install (fixed by retrying).

## Verdict
Buildah is the stronger choice for CI pipelines, security-conscious teams, and Kubernetes-native environments. Its daemonless, rootless architecture eliminates the attack surface introduced by running a privileged daemon and avoids the "docker group = root" risk. For production and regulated infrastructure, Buildah is preferable.
Docker remains the better choice for developers getting started with containers, local development workflows, and projects where the rich ecosystem of tutorials, compose tooling, and IDE integrations outweigh the security trade-offs.
