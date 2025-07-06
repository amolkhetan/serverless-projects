import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Describe all instances with the 'Action' tag
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Action',
                'Values': ['Auto-Stop', 'Auto-Start']
            },
            {
                'Name': 'tag:Ownedby',
                'Values': ['Amol']
            }
        ]
    )

    auto_stop_ids = []
    auto_start_ids = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            action = tags.get('Action')

            if action == 'Auto-Stop' and state == 'running':
                auto_stop_ids.append(instance_id)
            elif action == 'Auto-Start' and state == 'stopped':
                auto_start_ids.append(instance_id)

    if auto_stop_ids:
        print(f"Stopping instances: {auto_stop_ids}")
        ec2.stop_instances(InstanceIds=auto_stop_ids)

    if auto_start_ids:
        print(f"Starting instances: {auto_start_ids}")
        ec2.start_instances(InstanceIds=auto_start_ids)

    return {
        'statusCode': 200,
        'body': {
            'Stopped': [{'InstanceId': i[0], 'OwnedBy': i[1]} for i in auto_stop_ids],
            'Started': [{'InstanceId': i[0], 'OwnedBy': i[1]} for i in auto_start_ids]
        }
    }