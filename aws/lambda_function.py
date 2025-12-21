import json
import os
import boto3
from datetime import datetime

sns = boto3.client("sns")
sqs = boto3.client("sqs")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]

def lambda_handler(event, context):
    detail = event.get("detail", {})
    
    service_name = detail.get("serviceName", "Unknown")
    status = detail.get("status", "Unknown")
    time = detail.get("time", datetime.utcnow().isoformat())
    subject = f"{emoji} App Runner Deployment {status}"

    message = f"""
Deployment Notification

Service   : {service_name}
Status    : {status}
Time      : {time}
Region    : {event.get('region')}
Account   : {event.get('account')}
"""

    
    # Push event to SQS (optional)
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(event)
    )
    # Send Email + SMS via SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=subject,
        Message=message
    )

   

    return {
        "statusCode": 200,
        "message": "Notification sent successfully"
    }
