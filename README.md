# Taskboard: end-to-end DevOps project

Stack: nginx frontend, FastAPI backend, Postgres, Redis, Helm, GitHub Actions, Terraform (EKS + RDS), Prometheus.

## Run it in stages
1. Local: `make up` -> http://localhost:8080
2. Tests: `make test`
3. Kubernetes (kind): `make kind images deploy open` -> http://localhost:8080
   (frontend svc has no /api proxy in k8s; use ingress: install ingress-nginx, set `ingress.enabled=true`, add host to /etc/hosts)
4. Monitoring: `helm install mon prometheus-community/kube-prometheus-stack -n monitoring --create-namespace`, then deploy with `--set monitoring.serviceMonitor=true --set monitoring.alerts=true`
5. Cloud: `cd terraform && terraform init && terraform apply -var db_password=...`, then
   `aws eks update-kubeconfig --name taskboard`; store kubeconfig (base64) as `KUBECONFIG_B64` and RDS URL as `DATABASE_URL` in GitHub secrets. Push to main = deploy.

## Practice tasks
- Break it: `kubectl delete pod -l app=backend`, watch zero-downtime. Load test with `hey`/k6, watch HPA scale.
- Bad deploy: push an image that fails /readyz, confirm `--atomic` rolls back.
- Add: cert-manager TLS, external-secrets for DB password, Argo CD instead of `helm upgrade` in CI, Loki/ELK for logs.
