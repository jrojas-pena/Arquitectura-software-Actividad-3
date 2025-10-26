# 🧩 Proyecto: Arquitectura de Software — Actividad 3  
### Microservicio + Neo4j + Docker + Helm + ArgoCD + CI/CD (GHCR + GitHub Actions)

Este proyecto implementa un **microservicio FastAPI** conectado a una base de datos **Neo4j**, desplegado sobre **Kubernetes (Minikube)** y gestionado mediante **Helm y ArgoCD**, con un pipeline automatizado de **CI/CD** usando **GitHub Actions** y **GitHub Container Registry (GHCR)**.

---

## 🚀 Objetivo

Diseñar una arquitectura moderna basada en **microservicios**, aplicando buenas prácticas de **contenedorización**, **orquestación**, y **automatización del despliegue**.

---

## 🧰 Tecnologías utilizadas

| Componente | Herramienta |
|-------------|--------------|
| Lenguaje | Python 3.12 |
| Framework | FastAPI |
| Base de datos | Neo4j |
| Contenedores | Docker |
| Orquestador | Kubernetes (Minikube) |
| Configuración | Helm Charts |
| CD/Automatización | ArgoCD |
| CI/Build | GitHub Actions |
| Registro de imágenes | GHCR (GitHub Container Registry) |

---

## ⚙️ 1. Instalación de dependencias

### 🧱 Requisitos previos

En Fedora o WSL2 instala:

```bash
sudo dnf install -y docker minikube kubectl helm git
```

Inicia Docker:
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Reinicia sesión para aplicar los permisos.

---

## ☸️ 2. Iniciar Kubernetes con Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=4
```

Verifica:
```bash
kubectl get nodes
```

---

## 🧠 3. Instalar Neo4j en Kubernetes

Agrega el repositorio de Helm y actualiza:

```bash
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update
```

Instala Neo4j en Minikube:

```bash
helm install neo4j neo4j/neo4j   --set acceptLicenseAgreement=yes   --set neo4j.name=neo4j   --set neo4j.password=UniSabana2025   --set volumes.data.mode=defaultStorageClass   --namespace default
```

Verifica que esté corriendo:

```bash
kubectl get pods
kubectl get svc
```

Obtén acceso web:
```bash
minikube service neo4j-lb-neo4j -n default
```

💻 Abre [http://127.0.0.1:xxxxx](http://127.0.0.1:xxxxx) y entra con:
```
usuario: neo4j
contraseña: UniSabana2025
```

---

## 🧩 4. Estructura del proyecto

```bash
mcp-graph/
├─ services/
│  └─ mcp-graph-svc/
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ mcp_server.py
│     │  └─ neo4j_client.py
│     ├─ Dockerfile
│     └─ requirements.txt
├─ charts/
│  └─ mcp-graph-svc/
│     ├─ Chart.yaml
│     ├─ values.yaml
│     └─ templates/
│        ├─ _helpers.tpl
│        ├─ deployment.yaml
│        ├─ service.yaml
│        └─ secret.yaml
├─ argocd/
│  └─ app-mcp-graph-svc.yaml
└─ .github/
   └─ workflows/
      └─ ci-cd.yaml
```

---

## 🧱 5. Construcción y publicación de la imagen en GHCR

### 🔑 Autenticarse en GHCR

```bash
echo "<TOKEN>" | docker login ghcr.io -u <tu-usuario> --password-stdin
```

Crea el token desde  
👉 GitHub → Settings → Developer Settings → **Personal Access Token (classic)**  
con los permisos:
```
write:packages
read:packages
repo
```

### 🐳 Construir la imagen

```bash
docker build -t ghcr.io/<usuario>/mcp-graph-svc:0.1.0 ./services/mcp-graph-svc
```

### 📦 Publicarla en GHCR

```bash
docker push ghcr.io/<usuario>/mcp-graph-svc:0.1.0
```

---

## 🔁 6. CI/CD con GitHub Actions

### 🧩 Archivo: `.github/workflows/ci-cd.yaml`

El workflow:
1. Construye la imagen Docker.
2. Publica la imagen en GHCR.
3. ArgoCD sincroniza automáticamente el despliegue.

Para que funcione:
- En el repositorio → **Settings → Actions → General → Workflow permissions**  
  ✅ Habilita **Read and write permissions**.

- Añade un secreto (si usas PAT):  
  **Settings → Secrets → Actions → New repository secret**  
  Nombre: `GHCR_PAT`

---

## 🚀 7. Desplegar el microservicio con Helm

```bash
helm upgrade --install mcp-graph-svc ./charts/mcp-graph-svc   --set image.repository=ghcr.io/<usuario>/mcp-graph-svc   --set image.tag=0.1.0
```

Verifica:
```bash
kubectl get pods
kubectl get svc
```

Accede a la app:
```bash
minikube service mcp-graph-svc
```

---

## 🔄 8. Instalar y acceder a ArgoCD

Instala ArgoCD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Abre la UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

🔗 [https://localhost:8080](https://localhost:8080)

Credenciales:

```bash
usuario: admin
contraseña: $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
```

---

## 📊 9. Ver el estado del despliegue

```bash
argocd app list
argocd app get mcp-graph-svc
```

O desde la interfaz gráfica:  
verás el grafo del despliegue, los recursos creados y los estados:
- 🟢 **Healthy**
- 🟡 **Progressing**
- 🔴 **Degraded**

---

## 🧠 10. Sincronización automática

ArgoCD detecta los cambios en GitHub (nuevo tag, commit, o versión de imagen)  
y actualiza el clúster automáticamente gracias a:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

---

## ✅ 11. Verificación final

Comprueba que la app responde:

```bash
curl http://127.0.0.1:<puerto>/healthz
```

Deberías ver:
```json
{"status":"ok"}
```

---


