# 🐳 Running with Docker & Deploying to Other Platforms

This guide explains how to build, run, and deploy the UNO Minda API server using Docker. By containerizing the application, you can deploy it to any cloud provider or platform that supports Docker.

---

## 🛠️ Local Setup and Running

### 1. Build the Docker Image

Build the container image using the custom multi-stage Dockerfile:

```bash
docker build -t uno-minda-api .
```

### 2. Run the Container

Start the API server by passing your `.env` file containing your configurations (such as your `API_KEY`):

```bash
docker run -d \
  --name uno-minda-api-container \
  -p 8000:8000 \
  --env-file .env \
  uno-minda-api
```

The API will now be accessible at `http://localhost:8000`.

---

## 🚀 Running with Docker Compose (Recommended)

Docker Compose simplifies the process of starting the container by automatically reading the local `.env` file and mapping the ports.

### 1. Start the Server

```bash
docker compose up --build -d
```

- `--build`: Rebuilds the image if any source code or dependencies have changed.
- `-d`: Runs the container in detached (background) mode.

### 2. Check logs

To view the server output and incoming requests:

```bash
docker compose logs -f
```

### 3. Stop the Server

```bash
docker compose down
```

---

## ☁️ Deploying to Other Platforms

Since the application is containerized, you can deploy it to any platform that supports Docker. Here are instructions for popular platforms:

### 1. Render.com (Web Service)
1. Sign up/log in to [Render](https://render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Set the following options:
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `Dockerfile` (or leave default if at root)
5. Under **Environment Variables**, add the environment variables defined in `.env.example`:
   - `API_KEY` (Generate a strong 32-character key)
   - `ALLOWED_ORIGINS` (Set to `*` or your frontend domain)
   - `DEBUG` (`false`)
6. Click **Deploy Web Service**.

### 2. Railway.app
1. Sign up/log in to [Railway](https://railway.app).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your repository.
4. Railway will automatically detect the `Dockerfile` and configure a Docker-based deployment.
5. In the **Variables** tab of the service, add your environment variables (`API_KEY`, `ALLOWED_ORIGINS`, etc.).
6. In the **Settings** tab, make sure the exposed port is set to `8000`.
7. Railway will build and deploy the container automatically.

### 3. Koyeb
Koyeb is a high-performance serverless platform to deploy Docker containers from GitHub.
1. Sign up/log in to [Koyeb](https://www.koyeb.com).
2. Click **Create Service** and select **GitHub** as the deployment method.
3. Select your `UNO_MINDA` repository.
4. In the **Builder** section, select **Dockerfile**.
5. In the **Environment Variables** section, add:
   - `API_KEY` (Generate a strong 32-character key)
   - `ALLOWED_ORIGINS` (Set to `*` or your frontend domain)
   - `DEBUG` (`false`)
6. In the **Exposed Ports** section, set the port to `8000` (matching the Dockerfile container port) and set the protocol to `HTTP`.
7. Select your desired region and click **Deploy**.
### 4. AWS LightSail / ECS
1. Push your Docker image to **Amazon ECR** (Elastic Container Registry) or **Docker Hub**:
   ```bash
   docker tag uno-minda-api:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/uno-minda-api:latest
   docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/uno-minda-api:latest
   ```
2. Create an **ECS Task Definition** using the pushed image.
3. Configure the Container port to map `8000` to your desired host port.
4. Set the environment variables in the task definition config.
5. Launch the service.

---

## 🧪 Verification

After deploying or running locally, verify the API is functional:

```bash
# Verify health check (public)
curl http://localhost:8000/api/v1/health

# Verify protected endpoints (e.g. company profile)
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/api/v1/company/profile
```
