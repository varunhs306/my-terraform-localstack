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


data "archive_file" "zip_the_python_code" {
type        = "zip"
source_dir  = "./python"
output_path = "./python/pythonpackagesf1.zip"
}
 
resource "aws_lambda_function" "terraform_lambda_func" {
filename                       = data.archive_file.zip_the_python_code.output_path
function_name                  = "telegrambotfunction"
role                           = "arn:aws:iam::000000000000:role/dummy-role"
handler                        = "index.lambda_handler"
runtime                        = "python3.12"

# ✅ Environment variable for the bot token
  environment {
    variables = {
      BOT_TOKEN = "BOT_TOKEN"
    }
  }
}

