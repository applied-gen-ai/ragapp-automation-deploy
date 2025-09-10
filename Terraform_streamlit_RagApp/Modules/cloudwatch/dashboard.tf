resource "aws_cloudwatch_dashboard" "ecs_dashboard" {
  dashboard_name = "${var.ecs_service_name}-dashboard"

  dashboard_body = jsonencode({
    start = "-PT30M",
    widgets = [
      {
        type = "metric",
        x = 0, y = 0, width = 12, height = 6,
        properties = {
          view = "timeSeries",
          stacked = false,
          region = var.region,
          title = "ECS CPU Utilization (avg, last 30m)",
          period = 60,
          start = "-PT30M",
          metrics = [
            [ "AWS/ECS", "CPUUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name ]
          ]
        }
      },

      {
        type = "metric",
        x = 12, y = 0, width = 12, height = 6,
        properties = {
          view = "timeSeries",
          region = var.region,
          title = "ECS Memory Utilization (avg, last 30m)",
          period = 60,
          start = "-PT30M",
          metrics = [
            [ "AWS/ECS", "MemoryUtilization", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name ]
          ]
        }
      },

      {
        type = "metric",
        x = 0, y = 6, width = 12, height = 6,
        properties = {
          view = "timeSeries",
          region = var.region,
          title = "ALB Target Response Time (avg, last 30m)",
          period = 60,
          start = "-PT30M",
          metrics = [
            [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", var.alb_arn_suffix, "TargetGroup", var.alb_target_group_arn_suffix ]
          ]
        }
      },

      # Custom metrics: QuestionsAsked (count) and average length widgets
      {
  type = "metric",
  x = 12, y = 6, width = 12, height = 6,
  properties = {
    view = "timeSeries",
    region = var.region,
    title = "Users Asking Questions (last 30m)",
    period = 60,
    start = "-PT30M",
    metrics = [
      [ "CustomApp", "UsersAskingQuestions", { "stat": "Sum" } ]
    ]
  }
},

{
  type = "metric",
  x = 0, y = 12, width = 12, height = 6,
  properties = {
    view = "timeSeries",
    region = var.region,
    title = "Questions Asked (last 30m)",
    period = 60,
    start = "-PT30M",
    metrics = [
      [ "CustomApp", "QuestionsAsked", { "stat": "Sum" } ]
    ]
  }
},

{
  type = "metric",
  x = 12, y = 12, width = 12, height = 6,
  properties = {
    view = "timeSeries",
    region = var.region,
    title = "Avg Question Length (last 30m)",
    period = 60,
    start = "-PT30M",
    metrics = [
      [ "CustomApp", "AverageQuestionLength", { "stat": "Average" } ]
    ]
  }
},

{
  type = "metric",
  x = 0, y = 18, width = 12, height = 6,
  properties = {
    view = "timeSeries",
    region = var.region,
    title = "Avg Answer Length (last 30m)",
    period = 60,
    start = "-PT30M",
    metrics = [
      [ "CustomApp", "AverageAnswerLength", { "stat": "Average" } ]
    ]
  }
},

{
  type = "metric",
  x = 12, y = 18, width = 12, height = 6,
  properties = {
    view = "timeSeries",
    region = var.region,
    title = "Average Request Time (last 30m)",
    period = 60,
    start = "-PT30M",
    metrics = [
      [ "CustomApp", "AverageRequestTime", { "stat": "Average" } ]
    ]
  }
},


      # Log Insights widget example (shows last errors)
      {
        type = "log",
        x = 0, y = 18, width = 24, height = 6,
        properties = {
          query = "fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
          logGroupNames = [ var.log_group_name ],
          region = var.region,
          title = "Recent ERROR logs"
        }
      }
    ]
  })
}
