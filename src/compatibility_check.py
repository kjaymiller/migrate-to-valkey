import click
import valkey
import sys

@click.command(help="Analyze source database for migration compatibility")
@click.option("--source", default="valkey://localhost:6379", envvar="SOURCE_CONNECTION_STRING", help="Source connection string")
def compatibility_check_cmd(source):
    print("Connecting to source database...")
    client = valkey.from_url(source, decode_responses=True)

    try:
        client.ping()
    except Exception as e:
        print(f"❌ Failed to connect to source: {e}")
        sys.exit(1)

    print("\n=== Pre-Migration Compatibility Check ===")

    cursor = '0'
    total_keys = 0
    type_counts = {}
    standard_types = {"string", "list", "set", "zset", "hash", "stream", "none"}

    # Use pipelining to speed up type checking
    while cursor != 0:
        cursor, keys = client.scan(cursor=cursor, match='*', count=5000)
        if keys:
            pipe = client.pipeline(transaction=False)
            for key in keys:
                pipe.type(key)
            types = pipe.execute()

            total_keys += len(keys)
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1

    has_search = False
    search_indices = []
    try:
        search_indices = client.execute_command("FT._LIST")
        if search_indices:
            has_search = True
    except Exception:
        pass

    print(f"Total keys scanned: {total_keys}")
    if total_keys > 0:
        print("\nData Types Found:")
        for t, count in type_counts.items():
            print(f"  - {t}: {count} keys")

    warnings = []
    non_standard = set(type_counts.keys()) - standard_types
    if non_standard:
        # Check if the non-standard types include MBbloom-- (Bloom Filter)
        if "MBbloom--" in non_standard:
            print("ℹ️  Note: Bloom Filters (MBbloom--) detected. These require the RedisBloom module (supported by Aiven for Valkey).")
            non_standard.remove("MBbloom--")

        if non_standard:
            warnings.append(f"Extension Data Types Detected: {', '.join(non_standard)}. Ensure your target Valkey instance supports these (e.g. via the JSON module).")

    if has_search:
        warnings.append(f"Search Indices Detected ({', '.join(search_indices)}). Many Valkey providers (including Aiven) do not currently support RediSearch.")

    print("\n=== Compatibility Result ===")
    if not warnings and total_keys > 0:
        print("✅ SUCCESS: All data types and structures are 100% standard and compatible with Valkey!")
    elif total_keys == 0:
        print("ℹ️ Database is empty.")
    else:
        print("⚠️  WARNINGS: Migration may require special handling or might not be fully supported.")
        for i, w in enumerate(warnings, 1):
            print(f"  {i}. {w}")
        # Optionally exit with an error code if you want this to fail in CI
        sys.exit(1)

if __name__ == "__main__":
    compatibility_check_cmd()
