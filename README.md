# my-terraform-localstack

This repository demonstrates how to use Terraform to deploy AWS Lambda and related resources locally using [LocalStack](https://github.com/localstack/localstack). After deployment, you can interact wi[...]

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Terraform](https://www.terraform.io/downloads)
- [awslocal CLI](https://github.com/localstack/awscli-local) (`pip install awscli-local`)
- **Telegram Bot Token:**  
  Create a bot via [BotFather](https://t.me/BotFather) on Telegram to get your personal bot token.

> **Note:**  
> You do **not** need `git` or `docker compose` pre-installed for this specific flow.  
> **Before proceeding, replace the placeholder bot token in `main.tf` with your own Telegram bot token.**

---

## Running LocalStack and Deploying with Terraform

1. **Start LocalStack via Docker Compose**

   Make sure Docker is running, then start LocalStack:
   ```bash
   docker compose up -d
   ```

   LocalStack will now be running on your localhost (typically on port `4566`).

2. **Initialize and Apply Terraform**

   Run the following commands from the repository root to initialize and deploy your infrastructure to LocalStack:
   ```bash
   terraform init
   terraform apply
   ```
   Approve when prompted. This will provision the Lambda and related resources in your LocalStack environment.

---

## Interact with the Telegram Bot

You can now test and interact with the deployed Telegram bot at:  
👉 [https://t.me/Cl0udS0luti0n_bot](https://t.me/Cl0udS0luti0n_bot)

### Bot Commands

Type any of the commands below in the Telegram chat:

```
Here are my commands:
    /hello - Say hi
    /echo <text> - I’ll repeat your text
    /q - Get a random anime quote
    /roll - roll for a surprise
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
3. Interact with the Telegram bot at <https://t.me/Cl0udS0luti0n_bot>
4. Optionally, trigger the Lambda manually:
   ```
   awslocal lambda invoke --function-name telegrambotfunction response.json
   ```

---
## Screenshots
Screenshots folder contains the proof as screenshots with individual task subfolders
## License

This project is licensed under the MIT License.