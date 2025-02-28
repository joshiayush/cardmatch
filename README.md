# cardmatch
Find the best credit card according to your needs.

# Set the env
source .venv/bin/activate

# Start the devlopement server (Local)
uvicorn --reload main:app
http://localhost:8000


# Deploy in google cloud app engine
gcloud app deploy app.yaml

