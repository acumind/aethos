# Aethos Platform

A backend platform service that integrates with Azure AI Agent Service and uses AutoGen for agent orchestration. This project serves as the backend for Aethos web and mobile applications.

Features

RESTful API built with FastAPI
Integration with Azure AI Agent Service
Agent orchestration using AutoGen
Azure Blob Storage for file management
Azure SQL Database for structured data
Authentication and authorization
Containerization with Docker
CI/CD with GitHub Actions

Prerequisites

Python 3.10+
Azure subscription
Azure CLI
Docker (for containerization and local development)

Setup

1. Clone the repository
   bashgit clone https://github.com/yourusername/aethos.git
   cd aethos
2. Set up a virtual environment
   bashpython -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
3. Install dependencies
   bashpip install -r requirements.txt
4. Set up environment variables
   Copy the example environment file and fill in your values:
   bashcp .env.example .env
5. Set up Azure resources
   bashpython scripts/setup_azure.py
   Running Locally
   Using Python
   bashuvicorn app.main:app --reload
   Using Docker Compose
   bashdocker-compose up
   API Documentation
   Once the server is running, you can access the automatically generated API documentation:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

Testing
bashpytest
Deployment
Azure App Service
Configuration for deploying to Azure App Service is included in the GitHub Actions workflow files.
Kubernetes
bash# Instructions to be added
Project Structure
aethos-platform/
├── app/ # Application code
│ ├── api/ # API routes
│ ├── core/ # Core application code
│ ├── agents/ # Agent orchestration with AutoGen
│ ├── services/ # External services integration
│ ├── schemas/ # Pydantic schemas
│ ├── db/ # Database models
│ ├── middlewares/ # FastAPI middlewares
│ └── utils/ # Utility functions
├── tests/ # Test suite
└── scripts/ # Utility scripts
Contributing

Fork the repository
Create a feature branch: git checkout -b feature/my-feature
Commit your changes: git commit -am 'Add some feature'
Push to the branch: git push origin feature/my-feature
Submit a pull request

License
MIT
