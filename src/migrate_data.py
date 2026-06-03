import click
import valkey
from valkey.exceptions import ConnectionError
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")

@click.command(help="Logical migration tool: Dragonfly -> Valkey using DUMP/RESTORE")
@click.option("--source", default="valkey://localhost:6379", envvar="SOURCE_CONNECTION_STRING", help="Source connection string")
@click.option("--target", default="valkey://localhost:6379", envvar="TARGET_CONNECTION_STRING", help="Target connection string")
def migrate_data_cmd(source, target):
    logging.info("Connecting to databases...")

    try:
        source_client = valkey.from_url(source)
        target_client = valkey.from_url(target)

        # Test connections
        source_client.ping()
        target_client.ping()
    except ConnectionError as e:
        logging.error(f"❌ Connection error: {e}")
        sys.exit(1)

    logging.info("Starting logical migration (SCAN -> DUMP -> RESTORE)...")

    migrated_count = 0
    error_count = 0
    batch_size = 1000
    keys_batch = []

    def flush_batch(keys):
        nonlocal migrated_count, error_count
        if not keys:
            return

        # 1. Fetch DUMP and PTTL in a single network round-trip for the whole batch
        source_pipe = source_client.pipeline(transaction=False)
        for k in keys:
            source_pipe.dump(k)
            source_pipe.pttl(k)

        try:
            source_results = source_pipe.execute()
        except Exception as e:
            logging.error(f"⚠️ Failed to read batch from source: {e}")
            error_count += len(keys)
            return

        # 2. Queue RESTORE commands in a pipeline
        target_pipe = target_client.pipeline(transaction=False)
        valid_keys = 0
        for i, k in enumerate(keys):
            dump_data = source_results[i*2]
            pttl = source_results[i*2 + 1]

            if dump_data is None:
                continue  # Key disappeared between SCAN and DUMP

            if pttl < 0:
                pttl = 0

            target_pipe.restore(k, pttl, dump_data, replace=True)
            valid_keys += 1

        if valid_keys > 0:
            try:
                # 3. Execute all RESTORE commands in a single network round-trip
                target_pipe.execute()
                migrated_count += valid_keys
            except Exception as e:
                logging.warning(f"⚠️ Pipeline write failed, falling back to individual writes. Error: {e}")
                # Fallback to individual writes to identify the exact failing key
                for i, k in enumerate(keys):
                    dump_data = source_results[i*2]
                    pttl = source_results[i*2 + 1]

                    if dump_data is None:
                        continue
                    if pttl < 0:
                        pttl = 0

                    try:
                        target_client.restore(k, pttl, dump_data, replace=True)
                        migrated_count += 1
                    except Exception as inner_e:
                        logging.error(f"⚠️ Failed to migrate key {k}: {inner_e}")
                        error_count += 1

    # Iterate through all keys in the source database
    for key in source_client.scan_iter(match="*", count=batch_size):
        keys_batch.append(key)
        if len(keys_batch) >= batch_size:
            flush_batch(keys_batch)
            keys_batch = []
            logging.info(f"Progress: Processed {migrated_count + error_count} keys...")

    # Flush any remaining keys
    if keys_batch:
        flush_batch(keys_batch)
        logging.info(f"Progress: Processed {migrated_count + error_count} keys...")

    logging.info("\n--- Migration Complete ---")
    logging.info(f"✅ Successfully migrated keys: {migrated_count}")
    if error_count > 0:
        logging.info(f"❌ Failed to migrate keys: {error_count}")

if __name__ == "__main__":
    migrate_data_cmd()
