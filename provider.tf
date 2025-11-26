provider "aws" {
  # region and dummy credentials (LocalStack doesn't require real AWS creds)
  region     = "us-east-1"
  access_key = "test"
  secret_key = "test"

  # Skip checks that would try to contact real AWS account/metadata endpoints
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  # Explicitly point service endpoints to LocalStack (edge port 4566)
  endpoints {
    s3       = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    lambda  = "http://localhost:4566"
    iam      = "http://localhost:4566"
    sts      = "http://localhost:4566"
    
  }
   #setting for LocalStack S3 path-style URLs
    s3_use_path_style = true
}
