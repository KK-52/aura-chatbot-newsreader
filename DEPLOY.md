# Deploy to Google Cloud Run (Free)

This guide will help you deploy your RAG application to Google Cloud Run.

> [!WARNING]
> **Ephemeral Storage**: Cloud Run is stateless. The local `chroma_db` will be reset every time the application restarts. For persistent data, you should use an external database like Pinecone, Weaviate, or a managed ChromaDB instance.
>
> This deployment uses the **Source-based deployment** method which builds the container remotely on Google Cloud.

## Prerequisites

1.  **Google Cloud Project**: Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Billing Enabled**: You must enable billing, but Cloud Run has a generous free tier (2 million requests/month).
3.  **Google Cloud CLI**: Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

## Deployment Steps

### Option 1: Using the Helper Script (Windows)

1.  Open PowerShell in this directory.
2.  Run the deployment script:
    ```powershell
    ./deploy.ps1
    ```
3.  Follow the prompts to select your project and region.

### Option 2: Manual Deployment

1.  **Login to Google Cloud**:
    ```bash
    gcloud auth login
    ```

2.  **Set your project ID** (replace `YOUR_PROJECT_ID`):
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```

3.  **Deploy**:
    ```bash
    gcloud run deploy url-rag-service --source . --port 8080 --allow-unauthenticated --region us-central1
    ```
    - `url-rag-service`: The name of your service.
    - `--source .`: Use the current directory to build the container.
    - `--port 8080`: The port your app listens on.
    - `--allow-unauthenticated`: Makes the application public (remove if you want private access).

4.  **Wait for completion**: The command will output your Service URL (e.g., `https://url-rag-service-xyz.a.run.app`).

## Troubleshooting

-   **Build Failures**: Check the logs in the Cloud Console. Ensure `requirements.txt` is up to date.
-   **Service Unavailable**: Check if the service is scaling down to zero. Cold starts might take a few seconds.
-   **Memory Issues**: If the app crashes, you might need to increase memory limits (default is 512MB, you might need 1GB or 2GB for ML models).
    ```bash
    gcloud run services update url-rag-service --memory 1Gi
    ```
