resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/my-app"
  retention_in_days = 7
}

# 5. ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "my-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn = var.execution_role_arn
  task_role_arn      = var.task_role_arn


  container_definitions = jsonencode([{
    name  = "my-container"
    image = var.ecr_image_url # Replace with your container image
    portMappings = [{
      containerPort = 8501
      hostPort      = 8501
      protocol      = "tcp"
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
        awslogs-region        = "us-east-1"
        awslogs-stream-prefix = "ecs"
      }
    }
    secrets = [{
      name      = "aws-deploy"
      valueFrom = var.my_secret_value
    }]
  }])
}

# 7. Security Group for ALB & ECS
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow 8501"
  vpc_id = var.vpc_id


  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}