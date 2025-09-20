version: 0.2
env:
  variables:
    AWS_REGION: "us-east-1"
    AWS_ACCOUNT_ID: "826695974453"
    ECR_REPO_NAME: "streamlit-app-1"
    ECS_CLUSTER_NAME: "RagApp-fargate-cluster"
    ECS_SERVICE_NAME: "rag-app-service"
    ECS_CONTAINER_NAME: "my-container"
phases:
  pre_build:
    commands:
      - echo "=== PRE-BUILD PHASE STARTED ==="
      - echo "Checking AWS CLI configuration..."
      - aws --version
      - aws sts get-caller-identity
      - echo "Setting up variables..."
      - REPOSITORY_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
      - IMAGE_TAG_FULL="$CODEBUILD_RESOLVED_SOURCE_VERSION"
      - IMAGE_TAG="$(echo $IMAGE_TAG_FULL | cut -c 1-7)"
      - export REPOSITORY_URI
      - export IMAGE_TAG
      - echo "Repository URI=$REPOSITORY_URI"
      - echo "Image Tag=$IMAGE_TAG"
      - echo "Logging in to ECR..."
      - aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REPOSITORY_URI"
      - echo "Checking if ECR repository exists..."
      - aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" || aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION"
      - echo "Checking Dockerfile..."
      - test -f Dockerfile && echo "Dockerfile exists" || (echo "Dockerfile missing!" && exit 1)
  build:
    commands:
      - echo "=== BUILD PHASE STARTED ==="
      - echo "Listing files in build context..."
      - ls -al
      - echo "Checking if Dockerfile exists..."
      - cat Dockerfile || (echo "Dockerfile not found or not readable!" && exit 1)
      - echo "Checking Docker daemon..."
      - docker version
      - docker info
      - echo "Building Docker image..."
      - docker build --no-cache --progress=plain -t "$REPOSITORY_URI:$IMAGE_TAG" .
      - echo "Docker build completed, tagging image..."
      - docker tag "$REPOSITORY_URI:$IMAGE_TAG" "$REPOSITORY_URI:latest"
      - echo "Verifying image was created..."
      - docker images | grep "$ECR_REPO_NAME" || (echo "Image not found after build!" && exit 1)
  post_build:
    commands:
      - echo "=== POST-BUILD PHASE STARTED ==="
      - echo "Verifying images before push..."
      - docker images
      - echo "Pushing Docker image to ECR..."
      - docker push "$REPOSITORY_URI:$IMAGE_TAG" || (echo "Failed to push tagged image!" && exit 1)
      - docker push "$REPOSITORY_URI:latest" || (echo "Failed to push latest image!" && exit 1)
      - echo "Creating imagedefinitions.json..."
      - printf '[{"name":"%s","imageUri":"%s"}]' "$ECS_CONTAINER_NAME" "$REPOSITORY_URI:$IMAGE_TAG" > imagedefinitions.json
      - echo "Contents of imagedefinitions.json:"
      - cat imagedefinitions.json
      - echo "=== BUILD COMPLETED SUCCESSFULLY ==="
artifacts:
  files:
    - imagedefinitions.json
    - taskdef.json
    - appspec.yml
