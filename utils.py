from tenacity import retry, wait_exponential, stop_after_attempt
from setup_assets import generate_certificate as draw_certificate
import os
import boto3

@retry(wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3))
def robust_draw_certificate(name, achievement, date, certificate_id, output_path):
    print(f"Drawing certificate for {name} retry attempt {robust_draw_certificate.retry.statistics['attempt_number']}")

    draw_certificate(
        name=name, 
        achievement=achievement, 
        date=date, 
        certificate_id=certificate_id, 
        output_path=output_path
    )

def upload_certificate_to_cloud(local_file_path, file_name):
    s3_endpoint = os.getenv("SUPABASE_S3_ENDPOINT_URL")
    access_key = os.getenv("SUPABASE_S3_ACCESS_KEY")
    secret_key = os.getenv("SUPABASE_S3_SECRET_KEY")
    bucket = os.getenv("SUPABASE_S3_BUCKET_NAME", "certificates")

    if s3_endpoint and access_key and secret_key:
        s3 = boto3.client(
            "s3",
            endpoint_url=s3_endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto"
        )
        try:
            print(f"Uploading {file_name} to S3...")
            s3.upload_file(local_file_path, bucket, file_name, ExtraArgs={'ContentType': 'image/png'})

            return f"s3://{bucket}/{file_name}"
        except Exception as e:
            print(f"Failed to upload to S3: {e}")
            return local_file_path
    return local_file_path
