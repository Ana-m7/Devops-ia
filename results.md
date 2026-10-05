# Buildah vs Docker: Detailed Report

## 1. Objective
Compare two ways of building container images, **Buildah** (daemonless, rootless) and **Docker** (client plus root daemon), by building the same application with both tools and comparing build time, image size, runtime behaviour, and architecture and security characteristics.

## 2. Test Subject
A small Flask application, built from identical build files so that the build tool is the only variable.

| Item | Detail |
|---|---|
| App | `app/app.py`, Flask 3.0.3 (pinned in `app/requirements.txt`) |
| Routes | `/` (greeting), `/health` (`{"status":"ok"}`), `/whoami` (hostname and uid) |
| Port | 5000, bound to `0.0.0.0` |
| Base image | `docker.io/library/python:3.12-slim` |
| Build file | `Containerfile` and `Dockerfile`, byte-identical (verified with `diff`) |
| Build steps | `WORKDIR /app`, copy `requirements.txt`, `pip install --no-cache-dir`, copy `app.py`, `useradd -m appuser`, `USER appuser`, `EXPOSE 5000`, `CMD ["python", "app.py"]` |
| Security choice | The container runs as non-root user `appuser` |

## 3. Methodology

### 3.1 What was measured
1. **Build time**, cold and warm.
   - Cold: no cached layers, base image pulled from the registry.
   - Warm: the same build repeated immediately, to test layer caching.
2. **Image size**, as reported by each tool.
3. **Runtime behaviour**: the container starts, the three endpoints respond, and the process runs as a non-root user.
4. **Architecture and security**: daemon requirement and privilege model. These are taken from each tool's design and documentation, not measured.

### 3.2 How it was measured
- **Docker** (measured by Sofian): `time docker build -t flask-demo:docker .` for the cold and warm runs, then `docker history` and the image listing for size, then `curl` against the running container. Raw output is saved in `screenshots/docker/` (text files, not images).
- **Buildah** (measured by Person 1): `buildah build` using the same `Containerfile`, plus a second build using the step-by-step commands (`buildah from`, `run`, `copy`, `commit`). Only the resulting numbers and notes are recorded in this repository.

### 3.3 Test environments
| | Docker | Buildah |
|---|---|---|
| Machine | Apple Silicon Mac, 10 CPUs, 7.75 GiB RAM | WSL2 (per Person 1's notes) |
| Tool version | Docker 29.6.2 (Docker Desktop, BuildKit, overlayfs) | Not recorded |
| Architecture | aarch64 | Not recorded |
| Network | Not recorded | College network (DNS timeouts noted) |

## 4. Results

### 4.1 Timing and size
| Aspect | Buildah | Docker |
|---|---|---|
| Cold build | 27.020 s | 16.882 s |
| Warm build | 5.085 s (not a cache hit, see 5.1) | 0.826 s (all steps `CACHED`) |
| Image size | 137 MB | 235 MB disk usage (51.9 MB content size) |
| Build flexibility | Containerfile or scripted steps | Dockerfile |
| Ease of use | More concepts to learn | Simpler, more tutorials |
| CI/CD and Kubernetes fit | Strong (no privileged daemon) | Good, but needs Docker socket or DinD |

### 4.2 Docker details (from `screenshots/docker/`)
- **Cold build:** metadata lookup took 8.0 s and the base image download made up most of the 16.9 s. The `pip install` step took about 1.4 s.
- **Warm build:** all six build steps were served from cache, giving 0.83 s.
- **Layer sizes** (`docker history`): base Debian layer 110 MB, Python install 44.6 MB, apt packages 13.1 MB, Flask install 15.5 MB, app and user layers under 0.1 MB.
- **Runtime check:** `/` returned the greeting, `/health` returned `{"status":"ok"}`, and `/whoami` returned `{"hostname":"9e8bef93f74b","uid":1000}`. The uid of 1000 confirms the non-root user works.

### 4.3 Buildah details (from Person 1's notes)
- The step-by-step build (`from/run/copy/commit`) produced an identical 137 MB image to `buildah build`.
- `buildah build` does not cache layers unless `--layers` is passed.
- WSL2 shows a harmless "/ is not a shared mount" warning under rootless Podman.
- Flask ignores SIGTERM as PID 1, so `podman stop` waits 10 s before SIGKILL.
- DNS timeouts on the college network delayed the WSL install (fixed by retrying).

### 4.4 Architecture and security
| Aspect | Buildah | Docker |
|---|---|---|
| Architecture | Daemonless | Client plus root daemon |
| Root required | No (rootless by default) | Daemon runs as root (a rootless mode exists but is not the default) |
| Attack surface | No long-running privileged process | Privileged daemon and socket |
| Group-based risk | None | Membership of the `docker` group is effectively root |

## 5. Limitations
These affect how far the numbers can be trusted, and the comparison should be read with them in mind.

1. **Different machines.** Docker ran on an Apple Silicon Mac and Buildah on WSL2. CPU, architecture and disk differ, so build times are not directly comparable.
2. **Network-dominated cold builds.** Cold time mostly measures the base-image download, which depends on network speed (the Buildah run was on a college network with DNS issues).
3. **Unfair warm-build comparison.** Buildah's warm run was done without `--layers`, so it did not test caching. Docker's 0.83 s is a true cache hit.
4. **Size metrics differ.** Docker's 235 MB is Docker Desktop's disk-usage figure; its content size is 51.9 MB. The Buildah figure of 137 MB is likely a different metric on a different architecture, so the 137 vs 235 MB gap should not be read as Buildah producing a smaller image. The two builds use the same layers.
5. **Missing Buildah evidence.** There are no Buildah logs in this repository. The Buildah figures come from Person 1's notes and are not independently verifiable here.
6. **Single run.** Each timing is one measurement, with no repetition or averaging.
7. **Qualitative rows are opinions.** Ease of use, flexibility and CI fit are assessments, not measurements.

## 6. Observations on the demo app
Not part of the comparison, but relevant to production use:
- It uses Flask's development server (gunicorn would be preferred).
- There is no `HEALTHCHECK`, although `/health` exists.
- There is no `.dockerignore`.
- Only Flask is pinned; its transitive dependencies resolve at build time (for example Werkzeug 3.1.9).
- The base image is tagged, not pinned by digest.
- The `/` message says "built without Docker", but the same image was also built with Docker.

## 7. Recommendations for a fairer re-test
- Run both tools on the same machine and network.
- Use `buildah build --layers` for the warm run.
- Compare the same size metric, for example `docker image ls` against `podman images` on the same architecture.
- Repeat each build several times and report the average.
- Record tool versions and commit the Buildah logs under `screenshots/buildah/`.

## 8. Verdict
Buildah is the stronger choice for CI pipelines, security-conscious teams, and Kubernetes-native environments. Its daemonless, rootless architecture eliminates the attack surface introduced by running a privileged daemon and avoids the "docker group = root" risk. For production and regulated infrastructure, Buildah is preferable.

Docker remains the better choice for developers getting started with containers, local development workflows, and projects where the rich ecosystem of tutorials, compose tooling, and IDE integrations outweigh the security trade-offs.

The performance numbers do not decide between the two. Given the limitations above, the verdict rests mainly on the architecture and security differences.
