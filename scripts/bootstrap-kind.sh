#!/usr/bin/env bash
# Creates a local cluster with ingress, monitoring and Argo CD, then hands
# everything else to GitOps. Requires: docker, kind, kubectl, helm.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER=gitops-demo
INGRESS_NGINX_VERSION=controller-v1.12.0
ARGOCD_VERSION=v2.13.3

kind get clusters | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --config scripts/kind-config.yaml

echo ">> ingress-nginx"
kubectl apply -f "https://raw.githubusercontent.com/kubernetes/ingress-nginx/${INGRESS_NGINX_VERSION}/deploy/static/provider/kind/deploy.yaml"
kubectl wait -n ingress-nginx --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=180s

echo ">> kube-prometheus-stack"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f deploy/monitoring/kube-prometheus-stack-values.yaml --wait

echo ">> Argo CD"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd --server-side --force-conflicts \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"
kubectl wait -n argocd --for=condition=available deployment --all --timeout=300s

echo ">> Argo CD applications"
kubectl apply -f deploy/argocd/

echo
echo "Argo CD admin password:"
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
echo
echo "Argo CD : kubectl -n argocd port-forward svc/argocd-server 8443:443   -> https://localhost:8443"
echo "Grafana : kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80 -> http://localhost:3000"
echo "App     : http://dev.localtest.me"
