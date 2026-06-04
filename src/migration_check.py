import sys
import click
import valkey
from valkey.exceptions import ConnectionError

def get_version(client, name="Instance"):
    """Get the version of the service using valkey-py."""
    try:
        info = client.info()

        # Determine version based on the info dictionary keys
        if "valkey_version" in info:
            return info["valkey_version"]
        elif "dragonfly_version" in info:
            return info["dragonfly_version"]
        elif "redis_version" in info:
            return info["redis_version"]
        return "unknown"
    except Exception as e:
        print(f"❌ Failed to connect to {name} via valkey-py. Error: {e}")
        return "error"

def check_versions(source_client, target_client):
    """Fetch and compare versions of source and target using valkey-py."""
    print("Fetching versions via valkey-py...")
    source_version = get_version(source_client, "Source")
    target_version = get_version(target_client, "Target")

    print("=== Version Check ===")
    print(f"Source Version: {source_version}")
    print(f"Target Version: {target_version}")

    if source_version == "error" or target_version == "error":
        print("❌ Status: Could not determine versions.")
        sys.exit(1)

    print("✅ Status: Versions fetched successfully.")
    print("=====================\n")

def scan_schema(source_client, target_client):
    """Scan keys and their types from source and check against target."""
    print("=== Schema Scan ===")

    cursor = '0'
    matched_count = 0
    missing_count = 0
    mismatch_count = 0
    total_keys = 0

    # Track non-standard types that might indicate use of source extensions (JSON, Search, TimeSeries)
    standard_types = {"string", "list", "set", "zset", "hash", "stream", "none"}
    extension_type_counts = {}

    while cursor != 0:
        cursor, keys = source_client.scan(cursor=cursor, match='*', count=1000)

        for key in keys:
            total_keys += 1
            source_type = source_client.type(key)

            # Log extension types
            if source_type not in standard_types:
                extension_type_counts[source_type] = extension_type_counts.get(source_type, 0) + 1

            # Check if key exists in target
            if not target_client.exists(key):
                print(f"❌ Missing in target: '{key}' (Type: {source_type})")
                missing_count += 1
                continue

            # Check if type matches
            target_type = target_client.type(key)
            if source_type != target_type:
                print(f"⚠️ Type mismatch for '{key}': Source={source_type}, Target={target_type}")
                mismatch_count += 1
            else:
                matched_count += 1

    def check_search_indices():
        """Check for RediSearch indices on Source."""
        try:
            indices = source_client.execute_command("FT._LIST")
            if indices:
                print("\n⚠️  NOTE: Search Indices Detected!")
                print("Source supports FT.SEARCH, but Target may not support RediSearch.")
                print(f"Indices found: {', '.join(indices)}")
                return True
        except Exception:
            pass
        return False

    has_search = check_search_indices()

    print("\n--- Migration Check Summary ---")
    print(f"Total keys scanned: {total_keys}")
    print(f"Matching keys:      {matched_count}")
    print(f"Missing keys:       {missing_count}")
    print(f"Type mismatches:    {mismatch_count}")

    if extension_type_counts:
        print("\n⚠️  NOTE: Extension Data Types Detected!")
        print("Valkey supports the JSON module natively, but double check compatibility.")
        for ext_type, count in extension_type_counts.items():
            print(f"  - {ext_type}: {count} keys")

    print("-------------------------------")

    if missing_count > 0 or mismatch_count > 0:
        print("❌ Schema validation failed: Mismatches found between Source and Target.")
        sys.exit(1)
    elif extension_type_counts or has_search:
        print("✅ Schema validation passed, but ensure target Valkey supports the detected extensions.")
    else:
        print("✅ Success: Source and Target schemas match perfectly.")

@click.command(help="Migration check tool: Source -> Target")
@click.option("--source", required=True, envvar="SOURCE_CONNECTION_STRING", help="Source connection string (e.g., valkey://user:pass@host:port)")
@click.option("--target", required=True, envvar="TARGET_CONNECTION_STRING", help="Target connection string (e.g., valkey://user:pass@host:port)")
def migration_check_cmd(source, target):
    print("Connecting to databases...")
    # Initialize Valkey clients. decode_responses=True ensures we work with strings instead of bytes.
    source_client = valkey.from_url(source, decode_responses=True)
    target_client = valkey.from_url(target, decode_responses=True)

    # 1. Verify versions are compatible
    check_versions(source_client, target_client)

    # 2. Scan schema (keys and types) from source to ensure it matches target
    scan_schema(source_client, target_client)

if __name__ == "__main__":
    migration_check_cmd()
