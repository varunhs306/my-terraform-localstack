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
  hash_key       = "user_id"
  range_key      = "timestamp"
  billing_mode = "PAY_PER_REQUEST"

  global_secondary_index {
    name            = "user_id_index"
    hash_key        = "user_id"
    projection_type = "ALL"
    read_capacity   = 1
    write_capacity  = 1
  }
  attribute {
    name = "user_id"
    type = "S"
  }
    attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Environment = "local"
    ManagedBy   = "terraform"
  }
}

data "aws_iam_policy_document" "bot_dynamodb_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "bot_dynamodb_role" {
  name               = "bot-dynamodb-role"
  assume_role_policy = data.aws_iam_policy_document.bot_dynamodb_assume_role.json
}

data "aws_iam_policy_document" "bot_dynamodb_policy" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:DescribeTable",
      "dynamodb:DeleteItem"
    ]

    resources = [
      aws_dynamodb_table.my_table1.arn,
      "${aws_dynamodb_table.my_table1.arn}/*"
    ]
  }
}
resource "aws_iam_policy" "bot_dynamodb_policy" {
  name   = "bot-dynamodb-policy"
  policy = data.aws_iam_policy_document.bot_dynamodb_policy.json
}

resource "aws_iam_role_policy_attachment" "bot_dynamodb_policy_attach" {
  role       = aws_iam_role.bot_dynamodb_role.name
  policy_arn = aws_iam_policy.bot_dynamodb_policy.arn
}


data "archive_file" "zip_the_python_code" {
type        = "zip"
source_dir  = "./python"
output_path = "./python/pythonpackagesf1.zip"
}
 
resource "aws_lambda_function" "terraform_lambda_func" {
filename                       = data.archive_file.zip_the_python_code.output_path
function_name                  = "telegrambotfunction"
role                           = aws_iam_role.bot_dynamodb_role.arn
handler                        = "index.lambda_handler"
runtime                        = "python3.13"
timeout                        = 30


  environment {
    variables = {
      BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
      DDB_TABLE_NAME = "my-ls-table1"
    }
  }
}

