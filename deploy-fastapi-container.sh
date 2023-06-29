docker build . -f docker/Dockerfile.backend-fastapi -t shwastbackend
az acr login --name shwastcontainers
docker tag shwastbackend shwastcontainers.azurecr.io/shwastbackend
docker push shwastcontainers.azurecr.io/shwastbackend
