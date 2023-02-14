import boto3
import os 
def lambda_handler(event, context):
    access_key = os.environ['access_key'] 
    secret_key = os.environ['secret_key']
    region = os.environ['region']
    instance_id = os.environ['instance_id']
    
    ssm_client = boto3.client(
       "ssm",
       aws_access_key_id=access_key,
       aws_secret_access_key=secret_key,
       region_name=region
    )
    
    run_make_job = run_maker(instance_id, ssm_client)

    return
   
def run_maker(instance_id: str, client):
    commands = ['/usr/bin/python3 -u /home/ec2-user/make.py']
    response = client.send_command(
      DocumentName="AWS-RunShellScript",
      Parameters={"commands": commands},
      InstanceIds=[instance_id]
    )
    return response