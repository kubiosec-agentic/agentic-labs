#!/bin/bash

# Config
REGION="eu-west-1"
AMI_ID="ami-0df368112825f8d8f"
INSTANCE_TYPE="t2.medium"  
KEY_NAME="agentics-key"
INSTANCE_NAME="agentics-01"
VOLUME_SIZE=50

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --region $REGION --key-names $KEY_NAME &>/dev/null; then
  aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text \
    --region $REGION > ${KEY_NAME}.pem
  chmod 400 ${KEY_NAME}.pem
  echo "Created key pair and saved to ${KEY_NAME}.pem"
fi

# Get default VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
  --region $REGION \
  --filters Name=isDefault,Values=true \
  --query "Vpcs[0].VpcId" --output text)

# Get public subnet in default VPC
SUBNET_ID=$(aws ec2 describe-subnets \
  --region $REGION \
  --filters Name=vpc-id,Values=$VPC_ID Name=defaultForAz,Values=true \
  --query "Subnets[0].SubnetId" --output text)

# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances \
  --region $REGION \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --subnet-id $SUBNET_ID \
  --associate-public-ip-address \
  --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$VOLUME_SIZE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
  --query "Instances[0].InstanceId" --output text)

echo "Launched instance: $INSTANCE_ID"

# Wait for public IP
aws ec2 wait instance-running --region $REGION --instance-ids $INSTANCE_ID

PUBLIC_IP=$(aws ec2 describe-instances \
  --region $REGION \
  --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

echo "Instance is running at: $PUBLIC_IP"
echo "Connect with: ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
