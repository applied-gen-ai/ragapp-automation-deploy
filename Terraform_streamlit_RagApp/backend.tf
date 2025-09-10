terraform {
  backend "s3" {
    bucket = "new-account-terraform-state-bucket"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
