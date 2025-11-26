# my-terraform-localstack

This repository demonstrates how to use Terraform to deploy AWS Lambda and related resources locally using [LocalStack](https://github.com/localstack/localstack). After deployment, you can interact wi[...]

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Terraform](https://www.terraform.io/downloads)
- [awslocal CLI](https://github.com/localstack/awscli-local) (`pip install awscli-local`)
- **Telegram Bot Token:**  
  Create a bot via [BotFather](https://t.me/BotFather) on Telegram to get your personal bot token.

> **Note:**   
> **Before proceeding, replace the placeholder bot token in `main.tf` with your own Telegram bot token.**

---

## Running LocalStack and Deploying with Terraform

1. **Start LocalStack via Docker Compose**

   Make sure Docker is running, then start LocalStack:
   ```bash
   docker compose up
   ```

   LocalStack will now be running on your localhost (typically on port `4566`).
   >**Note:** Change the image name in docker yml file if you don't have localstack pro

   > ``` image: localstack/localstack-pro``` -> ```image: localstack/localstack```

2. **Initialize and Apply Terraform**

   Run the following commands from the repository root to initialize and deploy your infrastructure to LocalStack:
   ```bash
   terraform init
   terraform apply
   ```
   Approve when prompted. This will provision the Lambda and related resources in your LocalStack environment.

---

### Bot Commands

Type any of the commands below in the Telegram chat:

```
Here are my commands:
      /save <your data> - Save new data
      /list - View all your saved data
      /delete <number> - Delete a specific entry
      /help - Show this help message
```

---

## Manually Invoke Lambda Function

You can manually trigger the Lambda function in your LocalStack environment using `awslocal` 

```bash
awslocal lambda invoke --function-name telegrambotfunction response.json
```
---

## How to Run

1. Start LocalStack:
   ```
   docker compose up -d
   ```
2. Provision AWS resources with Terraform:
   ```
   terraform init
   terraform apply
   ```
3.Trigger the Lambda manually:
   ```
   awslocal lambda invoke --function-name telegrambotfunction response.json
   ```

---
## Screenshots
Screenshots folder contains the proof as screenshots with individual task subfolders
```
Task 3, Task 4,Task 5
```