# =======================================
# S3 Bucket
# =======================================
resource "aws_s3_bucket" "my_bucket1" {
  bucket = "my-ls-bucket-1"

  tags = {
    Environment = "local"
    ManagedBy   = "terraform"
  }
}

# =======================================
# DynamoDB Table
# =======================================
resource "aws_dynamodb_table" "my_table1" {
  name           = "my-ls-table1"
  hash_key       = "id"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = "local"
    ManagedBy   = "terraform"
  }
}
