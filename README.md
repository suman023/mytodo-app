# MyToDo App

A simple Todo application built with Flask and MySQL.

## Tech Stack
- **Backend:** Python Flask
- **Database:** MySQL
- **Container:** Docker
- **CI/CD:** Jenkins + SonarCloud + Trivy

## Project Structure
```
mytodo-app/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
├── init.sql
├── Dockerfile
├── docker-compose.yml
└── Jenkinsfile
```

## Run Locally
```bash
docker compose up -d
# Open: http://localhost:5000
```

## CI Pipeline (Jenkins)
1. Code Download
2. Python verify
3. pip install
4. SonarCloud scan
5. Docker build
6. Trivy scan
7. Docker login
8. Docker push → suman2304/mytodo
9. Update K8s manifest → triggers ArgoCD
