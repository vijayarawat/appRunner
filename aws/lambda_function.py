import json
import boto3
import os

def lambda_handler(event, context):
    # Extract deployment status from EventBridge event
    detail = event.get('detail', {})
    service_arn = detail.get('serviceArn', 'Unknown')
    operation_status = detail.get('operationStatus', 'Unknown')
    operation_type = detail.get('operationType', 'Unknown')

    # Prepare message
    message = {
        'serviceArn': service_arn,
        'operationStatus': operation_status,
        'operationType': operation_type,
        'timestamp': event.get('time', 'Unknown')
    }

    # Send to SQS
    sqs = boto3.client('sqs')
    queue_url = os.environ['SQS_QUEUE_URL']
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    # Send notification via SNS
    sns = boto3.client('sns')
    topic_arn = os.environ['SNS_TOPIC_ARN']
    sns.publish(
        TopicArn=topic_arn,
        Subject='App Runner Deployment Status',
        Message=json.dumps(message, indent=2)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent successfully')
    }