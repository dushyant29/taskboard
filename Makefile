up:        ; docker compose up --build
test:      ; cd backend && pip install -q -r requirements-dev.txt && pytest -q
kind:      ; kind create cluster --name tb
images:    ; docker build -t tb-backend:dev backend && docker build -t tb-frontend:dev frontend && kind load docker-image tb-backend:dev tb-frontend:dev --name tb
deploy:    ; helm upgrade --install tb helm/taskboard -n tb --create-namespace --set backend.image.repository=tb-backend --set backend.image.tag=dev --set frontend.image.repository=tb-frontend --set frontend.image.tag=dev --set ingress.enabled=false --rollback-on-failure
open:      ; kubectl -n tb port-forward svc/tb-frontend 8080:80
