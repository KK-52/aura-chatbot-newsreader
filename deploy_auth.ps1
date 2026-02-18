# PowerShell Script to Deploy to Google Cloud Run

Write-Host "=== Google Cloud Run Deployment Helper ===" -ForegroundColor Cyan

# Check if gcloud is installed
# Check if gcloud is installed
$gcloudBin = "gcloud"
if (-not (Get-Command "gcloud" -ErrorAction SilentlyContinue)) {
    $localPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    if (Test-Path $localPath) {
        $gcloudBin = $localPath
    } else {
        Write-Error "Google Cloud CLI (gcloud) is not installed. Please install it first: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
}

# Check login status
Write-Host "Checking gcloud authentication..." -ForegroundColor Yellow
$auth_status = & $gcloudBin auth list --format="value(account)" 2>&1
if (-not $auth_status) {
    Write-Host "Please log in to Google Cloud:" -ForegroundColor Yellow
    & $gcloudBin auth login
}

# Select Project
Write-Host "Getting project list..." -ForegroundColor Yellow
$projects = & $gcloudBin projects list --format="value(projectId)"
if (-not $projects) {
    Write-Error "No projects found. Please create a project in the Google Cloud Console."
    exit 1
}

Write-Host "`nAvailable Projects:" -ForegroundColor Green
$projects
$projectId = Read-Host "`nEnter the Project ID to use"

if (-not $projectId) {
    Write-Error "Project ID is required."
    exit 1
}

& $gcloudBin config set project $projectId

# Service Name
$serviceName = "url-rag-auth"
Write-Host "`nDeploying service '$serviceName'..." -ForegroundColor Cyan

# Deploy
# Using --source . to build from source (requires Cloud Build api enabled)
Write-Host "Note: This requires the 'Cloud Build API' and 'Cloud Run Admin API' to be enabled on your project." -ForegroundColor Magenta
Write-Host "Starting deployment... This may take a few minutes." -ForegroundColor Yellow

# Read .env file to get API keys
$envParams = @()

if (Test-Path ".env") {
    Write-Host "Reading .env file..." -ForegroundColor Cyan
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^(GROQ_API_KEY|GOOGLE_API_KEY|OPENAI_API_KEY)=(.*)$") {
            $key = $matches[1]
            $value = $matches[2]
            # Handle potential quotes
            $value = $value.Trim('"').Trim("'")
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                 $envParams += "$key=$value"
            }
        }
    }
} else {
    Write-Warning ".env file not found. API keys will not be set."
}

# Add Cloud Run specific env vars
$envParams += "CHROMA_DB_PATH=/tmp/chroma_db"

$envString = $envParams -join ","

Write-Host "Setting environment variables: $envString" -ForegroundColor DarkGray

& $gcloudBin run deploy $serviceName `
    --source . `
    --port 8080 `
    --allow-unauthenticated `
    --region us-central1 `
    --memory 512Mi `
    --min-instances 0 `
    --concurrency 80 `
    --set-env-vars $envString

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDeployment Successful!" -ForegroundColor Green
    Write-Host "Run '& $gcloudBin run services list' to see your URL."
} else {
    Write-Error "`nDeployment Failed. Please check the logs above."
}

Pause
