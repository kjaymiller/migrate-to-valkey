import sys
import click
import valkey
from valkey.exceptions import ConnectionError
import urllib.parse
import asyncio
from glide import GlideClient, GlideClientConfiguration, NodeAddress, ServerCredentials

async def get_version_via_glide(connection_string):
    """Get the version of the service using valkey-glide."""
    parsed = urllib.parse.urlparse(connection_string)
    host = parsed.hostname
    port = parsed.port or 6379
    password = parsed.password
    user = parsed.username
    scheme = parsed.scheme

    use_tls = scheme in ("valkeys", "rediss")
    credentials = None
    if user or password:
        credentials = ServerCredentials(username=user, password=password)

    config = GlideClientConfiguration(
        addresses=[NodeAddress(host, port)],
        use_tls=use_tls,
        credentials=credentials
    )

    try:
        client = await GlideClient.create(config)
        info_bytes = await client.info()
        await client.close()

        output = info_bytes.decode('utf-8', errors='ignore')
        version = "unknown"
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("valkey_version:"):
                return line.split(":")[1].strip()
            elif line.startswith("dragonfly_version:"):
                return line.split(":")[1].strip()
            elif line.startswith("redis_version:") and version == "unknown":
                version = line.split(":")[1].strip()
        return version
    except Exception as e:
        print(f"❌ Failed to connect to {host}:{port} via valkey-glide. Error: {e}")
        return "error"

def check_versions(source_url, target_url):
    """Fetch and compare versions of source and target using valkey-glide."""
    print("Fetching versions via valkey-glide...")
    source_version = asyncio.run(get_version_via_glide(source_url))
    target_version = asyncio.run(get_version_via_glide(target_url))

    print("=== Version Check ===")
    print(f"Source (Dragonfly) Version: {source_version}")
    print(f"Target (Valkey) Version:    {target_version}")

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

    # Track non-standard types that might indicate use of Dragonfly extensions (JSON, Search, TimeSeries)
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
        """Check for RediSearch indices on Dragonfly."""
        try:
            indices = source_client.execute_command("FT._LIST")
            if indices:
                print("\n⚠️  NOTE: Search Indices Detected!")
                print("Dragonfly supports FT.SEARCH, but Aiven for Valkey does not currently support RediSearch.")
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
        print("Aiven for Valkey supports the JSON module natively, but double check compatibility.")
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

@click.command(help="Migration check tool: Dragonfly -> Valkey")
@click.option("--source", default="valkey://localhost:6379", envvar="SOURCE_CONNECTION_STRING", help="Source connection string (e.g., valkey://user:pass@host:port)")
@click.option("--target", default="valkey://localhost:6379", envvar="TARGET_CONNECTION_STRING", help="Target connection string (e.g., valkey://user:pass@host:port)")
def migration_check_cmd(source, target):
    print("Connecting to databases...")
    # Initialize Valkey clients. decode_responses=True ensures we work with strings instead of bytes.
    source_client = valkey.from_url(source, decode_responses=True)
    target_client = valkey.from_url(target, decode_responses=True)

    # 1. Verify versions are compatible
    check_versions(source, target)

    # 2. Scan schema (keys and types) from source to ensure it matches target
    scan_schema(source_client, target_client)

if __name__ == "__main__":
    migration_check_cmd()
