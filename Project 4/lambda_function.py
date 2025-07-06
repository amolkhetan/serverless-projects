import boto3
from datetime import datetime, timezone, timedelta

# Replace with your EBS volume ID
VOLUME_ID = 'vol-0ee284fc5b82e3109'
RETENTION_DAYS = 6

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    created_snapshot_id = None
    deleted_snapshots = []

    # 1. Create a snapshot
    try:
        description = f"Automated snapshot of {VOLUME_ID} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        snapshot = ec2.create_snapshot(VolumeId=VOLUME_ID, Description=description)
        created_snapshot_id = snapshot['SnapshotId']
        print(f"✅ Created snapshot: {created_snapshot_id}")
    except Exception as e:
        print(f"❌ Error creating snapshot: {e}")

    # 2. Delete snapshots older than 30 days
    try:
        snapshots = ec2.describe_snapshots(
            Filters=[
                {'Name': 'volume-id', 'Values': [VOLUME_ID]},
                {'Name': 'description', 'Values': ['Automated snapshot*']}
            ],
            OwnerIds=['self']
        )['Snapshots']

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

        for snap in snapshots:
            start_time = snap['StartTime']
            if start_time < cutoff_date:
                ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])
                deleted_snapshots.append(snap['SnapshotId'])
                print(f"🗑️ Deleted old snapshot: {snap['SnapshotId']}")

    except Exception as e:
        print(f"❌ Error deleting old snapshots: {e}")

    return {
        'statusCode': 200,
        'body': {
            'created_snapshot': created_snapshot_id,
            'deleted_snapshots': deleted_snapshots
        }
    }