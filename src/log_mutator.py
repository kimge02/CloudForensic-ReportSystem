import json, glob, random, os
from datetime import datetime, timedelta

input_dir = "data/raw_logs/"
output_dir = "data/raw_logs/expanded/"
os.makedirs(output_dir, exist_ok=True)

regions = ["ap-northeast-2", "us-east-1", "eu-central-1", "ap-southeast-1"]
users = ["admin", "security_audit", "developer", "tester", "cloudops"]
services = [
    "ec2.amazonaws.com", "iam.amazonaws.com",
    "s3.amazonaws.com", "cloudtrail.amazonaws.com", "cloudwatch.amazonaws.com"
]

files = glob.glob(input_dir + "*.json")
print(f"[+] Found {len(files)} base logs")

count = 0
for f in files:
    with open(f, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"[!] Skipping invalid JSON: {f}")
            continue

    # CloudTrail 로그는 일반적으로 "Records" 리스트를 가짐
    if "Records" not in data:
        print(f"[!] No 'Records' in {f}, skipping...")
        continue

    for i, record in enumerate(data["Records"]):
        # userIdentity 없을 경우 생성
        if "userIdentity" not in record:
            record["userIdentity"] = {"userName": random.choice(users)}
        else:
            record["userIdentity"]["userName"] = random.choice(users)

        # 필드 안전하게 업데이트
        record["eventTime"] = (
            datetime.utcnow() - timedelta(minutes=random.randint(0, 10000))
        ).isoformat() + "Z"

        record["awsRegion"] = random.choice(regions)
        record["eventSource"] = random.choice(services)

        # 저장용 데이터 복사
        new_data = {"Records": [record]}

        new_name = f"{output_dir}log_mutated_{count}.json"
        with open(new_name, "w") as out:
            json.dump(new_data, out, indent=2)
        count += 1

print(f"[+] Generated {count} synthetic logs in {output_dir}")

