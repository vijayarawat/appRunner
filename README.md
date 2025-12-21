# Django Docker Web App

A simple Django web application containerized with Docker for easy deployment and scaling.

## Description

This project is a Django-based web application that demonstrates a basic setup with Docker. It includes a demo app with models, views, and templates.

## Architecture
![alt text](architecture/AppRunner.svg)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd django-docker-web-app
   ```

2. Build the Docker image:
   ```bash
   docker build -t django-app ./devops
   ```

## Running Locally

1. Run the application using Docker:
   ```bash
   docker run -p 8080:8080 django-app
   ```

2. Access the application at `http://localhost:8080`

For development without Docker:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Start the server:
   ```bash
   python manage.py runserver
   ```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment to AWS.

### Setup Instructions

1. **AWS ECR Repository**:
   - Create an ECR repository named `django-app` (or update the `ECR_REPOSITORY` environment variable in the workflow)
   - Note the ECR registry URL

2. **GitHub Secrets**:
   - Add the following secrets to your GitHub repository:
     - `AWS_ACCESS_KEY_ID`: Your AWS access key
     - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
   - Ensure the IAM user has permissions for ECR push and App Runner deployment

3. **Environment Variables**:
   - Update `AWS_REGION` in the workflow file to match your AWS region
   - Update `ECR_REPOSITORY` if your repository name differs

### AWS App Runner Deployment

- AWS App Runner automatically pulls the latest image from ECR
- Deployment is set to automatic mode, so new images with the `latest` tag trigger automatic deployment
- The service remains up and running with the latest deployed image

### Deployment Options

- **Automatic**: Enabled in AWS App Runner settings - images tagged `latest` are deployed automatically
- **Manual**: Can be triggered manually through the AWS Console or CLI if needed

## Notifications and Monitoring

The deployment process includes event-driven notifications:

- **EventBridge**: Monitors App Runner deployment events
- **Lambda Function**: Triggered by EventBridge when a deployment occurs
- **SQS Queue**: Receives deployment status events from Lambda
- **SNS and SES**: Sends email and SMS notifications to registered users about deployment status

When an image is deployed:
1. App Runner sends deployment status to EventBridge
2. EventBridge triggers the Lambda function
3. Lambda processes the event and sends it to the SQS queue
4. Notifications are sent via SNS (SMS) and SES (email) to registered users

## Setting up Notifications

Follow these steps to configure the event-driven notification system using AWS services:

### 1. Create an SQS Queue

1. Go to the AWS SQS Console
2. Click "Create queue"
3. Choose "Standard Queue"
4. Name it `app-runner-deployments` (or your preferred name)
5. Leave other settings as default
6. Note the Queue URL for later use

### 2. Create an SNS Topic

1. Go to the AWS SNS Console
2. Click "Create topic"
3. Choose "Standard"
4. Name it `deployment-notifications`
5. Create the topic
6. Note the Topic ARN

### 3. Subscribe to the SNS Topic

1. In the SNS Topic details, click "Create subscription"
2. Protocol: Email or SMS (create separate subscriptions for each)
3. Endpoint: Your email address or phone number (e.g., +1234567890 for SMS)
4. Repeat for additional subscribers

### 4. Create a Lambda Function

1. Go to the AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Name: `app-runner-deployment-handler`
5. Runtime: Python 3.9
6. Create a new role or use an existing one with SQS and SNS permissions
7. In the function code, paste the code from `aws/lambda_function.py`.

8. Add environment variables:
   - `SQS_QUEUE_URL`: The URL of your SQS queue
   - `SNS_TOPIC_ARN`: The ARN of your SNS topic

9. Set timeout to 30 seconds

### 5. Configure EventBridge Rule

1. Go to the AWS EventBridge Console
2. Click "Create rule"
3. Name: `app-runner-deployment-events`
4. Description: "Capture App Runner deployment events"
5. Rule type: "Rule with an event pattern"
6. Event source: "AWS events or EventBridge partner events"
7. Event pattern:

```json
{
  "source": ["aws.apprunner"],
  "detail-type": ["App Runner Service Operation Status Change"]
}
```

8. Select targets: Choose "Lambda function"
9. Function: Select `app-runner-deployment-handler`
10. Create the rule

### 6. Set up SES (if using email notifications)

1. Go to AWS SES Console
2. Verify your email address or domain
3. Create a receipt rule set if needed
4. Update the Lambda function to use SES instead of SNS for emails (see the code comments in `aws/lambda_function.py` for SES implementation)

### 7. Testing the Setup

1. Trigger a deployment by pushing a new image to ECR
2. Check CloudWatch logs for the Lambda function
3. Verify messages in SQS queue
4. Confirm notifications are received via email ans SMS


### GitHub Actions Workflow

The CI/CD pipeline (`.github/workflows/cicd.yml`) includes the following jobs:

1. **Test Job**:
   - Runs on every push and pull request to the `main` branch
   - Sets up Python environment
   - Installs dependencies
   - Runs Django migrations
   - Executes Django tests

2. **Build and Deploy Job**:
   - Runs after the test job passes
   - Configures AWS credentials
   - Logs into Amazon ECR
   - Builds the Docker image
   - Pushes the image with `latest` tag to ECR


## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── cicd.yml
├── aws/
│   └── lambda_function.py
├── Readme.md
├── requirements.txt
├── devops/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── demo/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   │       └── demo_site.html
│   └── devops/
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
└── db.sqlite3
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
