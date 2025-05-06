#!/bin/bash

set -e

# === Configuration ===
REGION="eu-west-1"
AMI_ID="ami-0df368112825f8d8f"
INSTANCE_TYPE="t2.medium"
KEY_NAME="agentics-key"
SECURITY_GROUP_NAME="agentics-ssh-sg"
VOLUME_SIZE=50
INSTANCE_COUNT=3  # Set your desired number of instances here
INSTANCE_PREFIX="agentics"

echo "Launching $INSTANCE_COUNT instance(s) in region $REGION..."

# === Setup Key Pair ===
if ! aws ec2 describe-key-pairs --region $REGION --key-names $KEY_NAME &>/dev/null; then
  echo "Creating key pair: $KEY_NAME"
  aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text \
    --region $REGION > "${KEY_NAME}.pem"
  chmod 400 "${KEY_NAME}.pem"
fi

# === Setup Network ===
VPC_ID=$(aws ec2 describe-vpcs \
  --region $REGION \
  --filters Name=isDefault,Values=true \
  --query "Vpcs[0].VpcId" --output text)

SUBNET_ID=$(aws ec2 describe-subnets \
  --region $REGION \
  --filters Name=defaultForAz,Values=true Name=vpc-id,Values=$VPC_ID \
  --query "Subnets[0].SubnetId" --output text)

# === Setup Security Group ===
SG_ID=$(aws ec2 describe-security-groups \
  --region $REGION \
  --filters Name=group-name,Values=$SECURITY_GROUP_NAME Name=vpc-id,Values=$VPC_ID \
  --query "SecurityGroups[0].GroupId" --output text 2>/dev/null || true)

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
  echo "Creating security group: $SECURITY_GROUP_NAME"
  SG_ID=$(aws ec2 create-security-group \
    --region $REGION \
    --group-name $SECURITY_GROUP_NAME \
    --description "Allow SSH access" \
    --vpc-id $VPC_ID \
    --query "GroupId" --output text)

  aws ec2 authorize-security-group-ingress \
    --region $REGION \
    --group-id $SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0
fi

# === Launch Instances in a Loop ===
for i in $(seq 1 $INSTANCE_COUNT); do
  INSTANCE_NAME=$(printf "%s-%02d" "$INSTANCE_PREFIX" "$i")
  echo "Launching instance: $INSTANCE_NAME"

  INSTANCE_ID=$(aws ec2 run-instances \
    --region $REGION \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --subnet-id $SUBNET_ID \
    --associate-public-ip-address \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$VOLUME_SIZE}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query "Instances[0].InstanceId" --output text)

  echo "Waiting for $INSTANCE_NAME ($INSTANCE_ID) to be running..."
  aws ec2 wait instance-running --region $REGION --instance-ids $INSTANCE_ID

  PUBLIC_IP=$(aws ec2 describe-instances \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

  echo "$INSTANCE_NAME is running at: $PUBLIC_IP"
  echo "Connect: ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
  echo "---------------------------------------------"
done
