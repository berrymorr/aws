#!/usr/bin/python3

import sys
import boto3

try:
    (tagName,tagValue) = sys.argv[1].split('=')
    newVolSize = int(sys.argv[2])
except:
    print(f"usage: {sys.argv[0]} TagName=TagValue NewSize")
    print(f"Resize EC2 with TagName=TagValue instance's root volume to NewSize")
    exit(10)


err = False

filter = [{
    'Name': f'tag:{tagName}', 
    'Values': [f'{tagValue}']
}]

ec2 = boto3.client('ec2')
response = ec2.describe_instances(Filters=filter)

for instance in response['Reservations'][0]['Instances']:
    print(instance['RootDeviceName'])
    if instance['RootDeviceType'] != 'ebs':
        continue
    for dev in instance['BlockDeviceMappings']:
        if dev['DeviceName'] == instance['RootDeviceName']:
            instance['RootDeviceId'] = dev['Ebs']['VolumeId']
    print(f"resizing instance's {instance['InstanceId']} volume {instance['RootDeviceId']} to {newVolSize}GB: ", end="")
    try:
        ec2.modify_volume(VolumeId=instance['RootDeviceId'],Size=newVolSize)
    except Exception as e:
        print(f"[ERROR] {e}")
        err = True
    else:
        print("[OK]")

if err:
    exit(1)
