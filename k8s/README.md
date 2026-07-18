# Kubernetes (local)

Plain-YAML manifests for running the full stack (Postgres, MinIO, backend, frontend)
on a local cluster (minikube, kind, or Docker Desktop's built-in Kubernetes). This is
the local dev/testing path only — it does not provision or target any cloud cluster.

## Quickstart (make)

```
make k8s-up       # build images, load into your cluster (auto-detects minikube/kind/docker-desktop), apply manifests
make k8s-status   # check pod status
make k8s-restart  # rebuild + reload images, rolling-restart backend/frontend after a code change
make k8s-down     # tear down (deletes the contoso namespace)
```

`k8s-load`/`k8s-up`/`k8s-restart` detect the cluster type from `kubectl config
current-context`: `minikube*` → `minikube image load`, `kind-*` → `kind load
docker-image` (set `KIND_CLUSTER=<name>` if your kind cluster isn't named `kind`),
`docker-desktop` → imports straight into its node container (see Notes below).
See below for the equivalent steps by hand, and for access/port-forwarding.

## One-time setup (manual equivalent)

Build the backend/frontend images (same Dockerfiles used by `docker-compose.yml`)
and load them into your cluster's own image store, so kubelet never tries to pull
them from a registry:

```
docker build -t contoso-backend:local ./backend
docker build -t contoso-frontend:local ./frontend
```

**minikube:**
```
minikube image load contoso-backend:local
minikube image load contoso-frontend:local
```

**kind:**
```
kind load docker-image contoso-backend:local --name <your-cluster-name>
kind load docker-image contoso-frontend:local --name <your-cluster-name>
```

**Docker Desktop:** its Kubernetes node doesn't share `docker build`'s image store
(unless "Use containerd for pulling and storing images" is on in Docker Desktop
settings), so a plain `docker build` isn't visible to the cluster on its own. The
node is itself a container (`desktop-control-plane`, running `kindest/node`), so it
can be loaded the same way `kind load docker-image` works internally:
```
docker save contoso-backend:local | docker exec -i desktop-control-plane ctr -n=k8s.io images import -
docker save contoso-frontend:local | docker exec -i desktop-control-plane ctr -n=k8s.io images import -
```

## Apply

```
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml -f k8s/secret.yaml
kubectl apply -f k8s/db.yaml -f k8s/minio.yaml -f k8s/backend.yaml -f k8s/frontend.yaml
```

Watch rollout:
```
kubectl -n contoso get pods -w
```

## Access

Everything is ClusterIP-only; reach it with `kubectl port-forward` (run each in its
own terminal). The ports match the app's existing localhost defaults, so no extra
env vars are needed on either side:

```
kubectl -n contoso port-forward svc/frontend 5173:5173
kubectl -n contoso port-forward svc/backend 8000:8000
kubectl -n contoso port-forward svc/minio 9000:9000 9001:9001
```

Then open `http://localhost:5173` (frontend talks to `http://127.0.0.1:8000` by
default — see `VITE_API_BASE` in `frontend/src/api/client.ts`). MinIO's console is
at `http://localhost:9001` (`minioadmin` / `minioadmin`, from `k8s/secret.yaml`).

## Rebuilding after a code change

Since images are loaded once into the cluster rather than pulled, a code change
needs a rebuild + reload + rollout restart — `make k8s-restart` does all three, or
by hand:

```
docker build -t contoso-backend:local ./backend
minikube image load contoso-backend:local   # or the kind/docker-desktop equivalent above
kubectl -n contoso rollout restart deployment/backend
```

## Notes

- Secrets in `k8s/secret.yaml` are dev-only placeholders checked into git —
  fine for a local cluster, not for anything shared or reachable outside your machine.
- `db` and `minio` use `ReadWriteOnce` PVCs sized for local dev (1Gi each).
- `backend`/`frontend` initContainers block on the services they depend on
  (`nc -z <svc> <port>`), since there's no direct k8s equivalent of
  docker-compose's `depends_on: condition: service_healthy`.
- The backend's readiness/liveness probes hit `/openapi.json` (FastAPI serves this
  by default), not `/` — the app has no root route, so probing `/` 404s and gets
  the pod killed as unhealthy.
- This replaces `ansible/` as the actively-maintained deployment path for local
  use. `ansible/` (EC2 + native install) is left in place, untouched, but is no
  longer documented as the recommended flow — see CLAUDE.md.