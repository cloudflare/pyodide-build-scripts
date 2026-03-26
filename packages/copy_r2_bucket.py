"""
Copy all objects from one R2 bucket into a subdirectory of another.

Supports both same-account and cross-account copies.

Same-account usage (server-side copy):
    python copy_r2_bucket.py --src SOURCE --dest DEST --prefix PREFIX

Cross-account usage (streams through runner):
    python copy_r2_bucket.py --src SOURCE --dest DEST --prefix PREFIX

Requires environment variables:
    # Destination (or shared) credentials
    R2_ACCOUNT_ID
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY

    # Source credentials (optional — enables cross-account mode)
    R2_SRC_ACCOUNT_ID
    R2_SRC_ACCESS_KEY_ID
    R2_SRC_SECRET_ACCESS_KEY
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
        "--src-prefix",
        default="",
        help="Only copy objects matching this source key prefix",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be copied without copying",
    )
    parser.add_argument(
        "--start-after",
        default="",
        help="Resume listing after this key (for resuming interrupted runs)",
    )
    return parser.parse_args()


def make_s3_client(account_id: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def get_s3_clients() -> tuple:
    """Return (src_s3, dest_s3, is_cross_account).

    If R2_SRC_* env vars are set, creates separate clients for source and
    destination (cross-account mode). Otherwise, returns the same client
    for both (same-account mode).
    """
    dest_account_id = os.environ["R2_ACCOUNT_ID"]
    dest_access_key = os.environ["R2_ACCESS_KEY_ID"]
    dest_secret_key = os.environ["R2_SECRET_ACCESS_KEY"]
    dest_s3 = make_s3_client(dest_account_id, dest_access_key, dest_secret_key)

    src_account_id = os.environ.get("R2_SRC_ACCOUNT_ID")
    src_access_key = os.environ.get("R2_SRC_ACCESS_KEY_ID")
    src_secret_key = os.environ.get("R2_SRC_SECRET_ACCESS_KEY")

    if src_account_id and src_access_key and src_secret_key:
        src_s3 = make_s3_client(src_account_id, src_access_key, src_secret_key)
        return src_s3, dest_s3, True

    return dest_s3, dest_s3, False


def list_all_objects(
    s3, bucket: str, start_after: str = "", src_prefix: str = ""
) -> list[dict]:
    objects = []
    kwargs: dict = {"Bucket": bucket}
    if src_prefix:
        kwargs["Prefix"] = src_prefix
    if start_after:
        kwargs["StartAfter"] = start_after

    while True:
        response = s3.list_objects_v2(**kwargs)

        if "Contents" not in response:
            break

        objects.extend(response["Contents"])

        if response.get("IsTruncated"):
            kwargs["ContinuationToken"] = response["NextContinuationToken"]
        else:
            break

    return objects


def copy_objects_same_account(
    s3,
    src_bucket: str,
    dest_bucket: str,
    prefix: str,
    objects: list[dict],
    *,
    dry_run: bool = False,
) -> None:
    """Server-side copy within the same account (original behavior)."""
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


def copy_objects_cross_account(
    src_s3,
    dest_s3,
    src_bucket: str,
    dest_bucket: str,
    prefix: str,
    objects: list[dict],
    *,
    dry_run: bool = False,
) -> None:
    """Download from source account, upload to destination account."""
    total = len(objects)
    failed = []

    for i, obj in enumerate(objects, 1):
        src_key = obj["Key"]
        dest_key = prefix + src_key

        if dry_run:
            print(f"[{i}/{total}] Would transfer {src_key} -> {dest_key}")
            continue

        size_mb = obj.get("Size", 0) / (1024 * 1024)
        print(f"[{i}/{total}] Transferring {src_key} -> {dest_key} ({size_mb:.1f} MB)")

        try:
            response = src_s3.get_object(Bucket=src_bucket, Key=src_key)
            dest_s3.upload_fileobj(
                response["Body"],
                dest_bucket,
                dest_key,
                ExtraArgs={
                    "ContentType": response.get(
                        "ContentType", "application/octet-stream"
                    ),
                },
            )
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append(src_key)

    if failed:
        raise Exception(f"Failed to transfer {len(failed)} objects: {failed}")


def main():
    args = parse_args()
    prefix = args.prefix if args.prefix.endswith("/") else args.prefix + "/"

    src_s3, dest_s3, is_cross_account = get_s3_clients()
    mode = "cross-account" if is_cross_account else "same-account"
    print(f"Mode: {mode}")

    src_label = f"{args.src}/{args.src_prefix}*" if args.src_prefix else args.src
    print(f"Listing objects in {src_label}...")
    objects = list_all_objects(
        src_s3, args.src, start_after=args.start_after, src_prefix=args.src_prefix
    )
    print(f"Found {len(objects)} objects.")

    if args.start_after:
        print(f"(Resuming after key: {args.start_after})")

    if not objects:
        print("Nothing to copy.")
        return

    if args.dry_run:
        print("DRY RUN — no objects will be copied.")

    if is_cross_account:
        copy_objects_cross_account(
            src_s3, dest_s3, args.src, args.dest, prefix, objects, dry_run=args.dry_run
        )
    else:
        copy_objects_same_account(
            src_s3, args.src, args.dest, prefix, objects, dry_run=args.dry_run
        )

    print("Done." if not args.dry_run else "Dry run complete.")


if __name__ == "__main__":
    main()
