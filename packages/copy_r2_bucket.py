"""
Copy all objects from one R2 bucket into a subdirectory of another.

Usage:
    python copy_r2_bucket.py --src SOURCE --dest DEST --prefix PREFIX

Requires environment variables:
    R2_ACCOUNT_ID
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
"""

import argparse
import os

import boto3


def parse_args():
    parser = argparse.ArgumentParser(description="Copy all objects between R2 buckets")
    parser.add_argument("--src", required=True, help="Source bucket name")
    parser.add_argument("--dest", required=True, help="Destination bucket name")
    parser.add_argument(
        "--prefix", required=True, help="Destination key prefix (subdirectory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be copied without copying",
    )
    return parser.parse_args()


def get_s3_client():
    r2_account_id = os.environ["R2_ACCOUNT_ID"]
    r2_access_key = os.environ["R2_ACCESS_KEY_ID"]
    r2_secret_access_key = os.environ["R2_SECRET_ACCESS_KEY"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_access_key,
        region_name="auto",
    )


def list_all_objects(s3, bucket: str) -> list[dict]:
    objects = []
    continuation_token = None

    while True:
        kwargs = {"Bucket": bucket}
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token

        response = s3.list_objects_v2(**kwargs)

        if "Contents" not in response:
            break

        objects.extend(response["Contents"])

        if response.get("IsTruncated"):
            continuation_token = response["NextContinuationToken"]
        else:
            break

    return objects


def copy_objects(
    s3,
    src_bucket: str,
    dest_bucket: str,
    prefix: str,
    objects: list[dict],
    *,
    dry_run: bool = False,
) -> None:
    total = len(objects)
    failed = []

    for i, obj in enumerate(objects, 1):
        src_key = obj["Key"]
        dest_key = prefix + src_key

        if dry_run:
            print(f"[{i}/{total}] Would copy {src_key} -> {dest_key}")
            continue

        print(f"[{i}/{total}] Copying {src_key} -> {dest_key}")

        try:
            s3.copy_object(
                Bucket=dest_bucket,
                Key=dest_key,
                CopySource={"Bucket": src_bucket, "Key": src_key},
            )
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append(src_key)

    if failed:
        raise Exception(f"Failed to copy {len(failed)} objects: {failed}")


def main():
    args = parse_args()
    prefix = args.prefix if args.prefix.endswith("/") else args.prefix + "/"

    s3 = get_s3_client()

    print(f"Listing objects in {args.src}...")
    objects = list_all_objects(s3, args.src)
    print(f"Found {len(objects)} objects.")

    if not objects:
        print("Nothing to copy.")
        return

    if args.dry_run:
        print("DRY RUN — no objects will be copied.")

    copy_objects(s3, args.src, args.dest, prefix, objects, dry_run=args.dry_run)
    print("Done." if not args.dry_run else "Dry run complete.")


if __name__ == "__main__":
    main()
