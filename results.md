# Buildah vs Docker: Results

| Measurement | Buildah | Docker |
|---|---|---|
| Cold build (with base image pull) | 27.020s | |
| Rebuild, default caching | 15.209s (no layer cache by default) | |
| First build with layer caching | 25.842s (`--layers`) | |
| Cached rebuild | 5.085s (`--layers`) | |
| Image size | 137 MB (base 124 MB) | |
| Daemon required | No | |
| Runs as root on host | No (app runs as host UID 100999) | |
| Image storage | ~/.local/share/containers | |

## Notes from Person 1
- `buildah build` does not cache layers unless `--layers` is passed.
- The step-by-step build (`buildah from/run/copy/commit`) produced an identical 137 MB image.
- WSL2 shows a harmless "/ is not a shared mount" warning under rootless Podman.
- Flask ignores SIGTERM as PID 1, so `podman stop` waits 10s before SIGKILL.
- DNS timeouts on the college network delayed the WSL install (fixed by retrying).
