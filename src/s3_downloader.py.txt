import boto3
import os

BUCKET_NAME = "cloudtrail-log-demo-goeun"   # 네가 만든 버킷 이름
DOWNLOAD_DIR = "data/raw_logs"

def download_latest_logs():
    s3 = boto3.client("s3")

    # 폴더 없으면 생성
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # S3 객체 목록 가져오기
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="AWSLogs")

    if "Contents" not in objects:
        print("⚠ No CloudTrail logs found in S3 yet.")
        return

    for obj in objects["Contents"]:
        key = obj["Key"]
        local_path = os.path.join(DOWNLOAD_DIR, key.replace("/", "_"))

        # 이미 다운로드한 파일이면 skip
        if os.path.exists(local_path):
            continue

        print(f"⬇ Downloading: {key}")
        s3.download_file(BUCKET_NAME, key, local_path)

    print("✅ S3 download complete!")
