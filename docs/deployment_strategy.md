# Deployment Strategy

## 1. Infrastructure Overview (Cloud Agnostic - AWS/GCP)

### Containers & Orchestration
*   **Dockerization**: Each service (Backend API, AI Service, Frontend) will be containerized using Docker.
*   **Orchestration**: Kubernetes (EKS/GKE) for scaling, or Docker Compose for smaller deployments/MVP.

### Continuous Integration / Continuous Deployment (CI/CD)
*   **GitHub Actions**:
    *   On Push: Run unit tests (Pytest).
    *   On Merge to Main: Build Docker images.
    *   Deploy: Push images to ECR/GCR and update clusters.

## 2. Server Configuration

### Backend (FastAPI)
*   Run with `gunicorn` managing `uvicorn` workers.
*   Autoscaling based on CPU utilization > 70%.
*   **AI Service Node Group**: Deploy the Face Recognition service on nodes with GPU support (e.g., AWS g4dn.xlarge) or high-compute instances if using CPU-optimized models (DeepFace/OpenVINO).

### Database (PostgreSQL)
*   Managed instance (RDS / Cloud SQL) with automated backups.
*   Read Replicas enabled for heavy reporting/read queries from Admin Panel.

### Storage
*   **Images**: AWS S3 with Lifecycle policies to move old logs to Glacier.
*   **Encryption**: Server-side encryption (SSE-S3) enabled.

## 3. Deployment Steps

1.  **Build Phase**
    ```bash
    docker build -t attendance-backend ./backend
    docker build -t attendance-admin ./frontend-admin
    ```

2.  **Infrastructure Provisioning (Terraform)**
    *   Provision VPC, Subnets, Security Groups.
    *   Spin up RDS (Postgres) and Redis (ElastiCache).

3.  **Application Deployment**
    *   Deploy Backend Services.
    *   Migrate Database (`alembic upgrade head`).
    *   Deploy Frontend to Static Hosting (S3 + CloudFront / Firebase Hosting).

## 4. Scalability Plan (10,000+ Employees)

*   **Database Partitioning**: Partition `attendance_logs` by month/year to keep index sizes manageable.
*   **Caching**: Heavy use of Redis for checking "Is Employee Present Today?" preventing DB hits.
*   **Queue System**: Use Celery/BullMQ for generating payroll PDFs and Excel exports asynchronously to avoid blocking the main API.

## 5. Security Hardening
*   **WAF (Web Application Firewall)**: Protect against SQL injection and DDOS.
*   **Rate Limiting**: Implement at API Gateway level (Nginx/Kong) to prevent brute force on login.
*   **Secrets Management**: Use AWS Secrets Manager / HashiCorp Vault. Do NOT hardcode API keys.
