# JIT Workflow Execution

---
NOTE: This is the public variant of the JIT Workflow Execution repository. The public variant is created to wipe the change history. If access the private variant with history is desired, please contact the authors.
---

## Overview

**JIT Workflow Execution** is an API-driven service designed to manage just-in-time execution of workflows. It enables users to initiate, monitor, and control workflows dynamically, with flexible integration into storage solutions and external services.

The project is containerized using Docker, and its continuous integration and deployment are automated through GitHub Actions. The system is designed for modularity and can be adapted or extended based on future requirements.

---

## Project Layout

The repository is organized into key components to ensure a clean separation of concerns:

- `api/`  
  Contains the core Flask API responsible for workflow execution, storage interactions (via `rclone`), and management of workflow lifecycles.  
  The API is the main interface for external clients to interact with the service.

- `benchmark/`  
  A suite of performance benchmarking tools and scripts. These are used to evaluate and test the scalability and responsiveness of the API and underlying systems.

- `POC/`  
  Proof-of-concept implementations and prototypes. This directory contains experimental features or early-stage ideas that may be integrated into the core project in the future. Currently only an agro-API POC is available, this is because most POC's are already fully integrated within the product and were deemed duplication's.

---

## API Overview

The Flask-based API is responsible for orchestrating workflow executions. Its main capabilities include:

- Triggering workflow executions on demand
- Monitoring and managing workflow status
- Handling input/output data transfer, including remote storage via `rclone`

### Modular Potential  
The current implementation combines multiple responsibilities into a single Flask API. For future improvements, the service can be split into **two separate APIs**:
1. A **Control API** to manage workflows and metadata
2. A **Data API** to handle file transfers and integration with remote storage (e.g., `rclone`)

This separation would improve maintainability and scalability as the system grows.

---

## Local Development Setup

### Prerequisites

- **MongoDB Instance**  
  The application is currently tightly integrated with MongoDB for its workflow state management and metadata storage. Developers are expected to configure and run a MongoDB instance. How this is set up is left to the external party and can be customized as needed.

- **Python 3.x**
- **Docker** (optional for containerized runs)
- **rclone** (optional for remote storage management)

### Setup Instructions

The current setup is not easy as there is a tight integration with MongoDB hosted on AWS. This makes the code less portable. Our advice is to refactor this code or edit the code to match your MongoDB instance.

You can run the application either **natively** on your machine or by using the provided **Dockerfile** for a containerized environment. Below are both options:

---

#### Native Setup

1. **Configure MongoDB**  
   Ensure a MongoDB instance is running and accessible.  
   The application depends on MongoDB for storing workflow state and metadata.  
   It is up to the external party to configure this MongoDB instance according to their needs.  
   Update the connection details in `config.py` or pass them as environment variables.

2. **Set up your Python environment**  
   Create and activate a virtual environment, then install the dependencies:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the Flask API locally**  
   Start the development server:  
   ```bash
   python3 -m flask run
   ```

4. **(Optional) Configure and Use rclone**  
   The system supports file synchronization and management through `rclone`.  
   While it can be integrated directly into the Flask API workflow, it is also possible to run `rclone` as a **standalone service** for better modularity and scalability.  
   Refer to the setup scripts located in `local_setup/`:
   - `setupRClone.sh` – to configure rclone for your remote storage
   - `cleanRClone.sh` – to remove or reset rclone configurations

---

#### Dockerized Setup (Recommended)

To simplify deployment and ensure consistency across environments, you can build and run the API service using Docker.

1. **Build the Docker image**  
   Run the following command in the root of the `api/` directory where the `Dockerfile` is located:  
   ```bash
   docker build -t jit-workflow-api .
   ```

2. **Run the Docker container**  
   Start the container, making sure to provide the necessary environment variables for MongoDB and any other configuration:  
   ```bash
   docker run -d \
     --name jit-workflow-api \
     -p 5000:5000 \
     -e MONGO_URI="mongodb://<your-mongo-host>:<port>/<db>" \
     jit-workflow-api
   ```

3. **(Optional) Use docker-compose for multi-service setup**  
   If you want to manage MongoDB, the API, and potentially the rclone service in a single setup, consider writing a `docker-compose.yml` file.  
   This makes managing multiple containers easier, especially for local development or testing environments.

---

#### Notes

- **MongoDB**  
  The Docker container assumes you are either connecting to an external MongoDB instance or running MongoDB in another container. Make sure the connection details are correctly provided.

- **rclone Manager**  
  You can run `rclone` directly in the container as part of the Flask API or separately as a dedicated container or service.  
  For standalone deployment, use the provided `setupRClone.sh` and `cleanRClone.sh` scripts in `local_setup/`.

---

This Docker-based approach simplifies running the service locally without needing to manually install Python packages and manage dependencies.

## Deployment via GitHub Actions

The repository includes a GitHub Actions workflow for automated testing and deployment.  
Key steps in the CI/CD pipeline include:
- Running unit and integration tests
- Building Docker images
- Pushing images to the configured container registry
- Deploying to staging or production environments (as applicable)

### Required Secrets

The following secrets must be configured in GitHub before running deployments:  
- `DOCKERHUB_USERNAME`  
- `DOCKERHUB_TOKEN`  
- `DEPLOYMENT_PRIVATE_KEY` (for server access if needed)  
- `RCLONE_CONFIG` (if applicable for remote storage integration)  

Secrets can be configured in GitHub under:  
**Repository Settings > Secrets and variables > Actions**

---

## Private Keys and Sensitive Data

- Sensitive configuration files (e.g., `replication_settings.json.enc`) are encrypted and must be securely managed.
- Private keys and encrypted credentials are stored as GitHub Actions secrets.
- No sensitive data or private keys should be committed to the repository.

---

## Future Considerations

- **API Splitting**  
  For future scalability and clearer separation of concerns, consider splitting the current Flask API into two distinct services:
  1. **Control API** – manages workflow lifecycle and metadata
  2. **Data API** – handles file transfer operations and remote storage integration (via `rclone`)

- **MongoDB Abstraction**  
  Consider abstracting the database layer in future releases to support alternative backends beyond MongoDB.

- **Enhanced rclone Management**  
  Operating the rclone manager as a separate microservice can offer improved performance, maintainability, and scalability.

---

## License

This project is licensed under the terms of the [LICENSE](../license.md) file located at the root of this repository.
