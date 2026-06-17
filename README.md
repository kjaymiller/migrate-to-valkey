# Migration to Valkey Project

This project contains tools and instructions to help migrate data from Redis or Dragonfly (or between any Redis-compatible databases) to Valkey .

## Quick Migration Guide

Use this table to gauge what will migrate cleanly before you start. The `mise run check` task scans your source database and flags anything in the last two categories.

| Data type / feature | Status | Notes |
| --- | --- | --- |
| String | ✅ Works | Core type, no modules needed |
| List | ✅ Works | Core type |
| Set | ✅ Works | Core type |
| Sorted Set (`zset`) | ✅ Works | Core type |
| Hash | ✅ Works | Core type |
| Stream | ✅ Works | Core type |
| HyperLogLog | ✅ Works | Stored as strings |
| Geospatial (GEO) | ✅ Works | Backed by sorted sets |
| Bitmaps | ✅ Works | Backed by strings |
| JSON (`JSON.*`) | 🧩 Needs module | Requires the JSON module on the target Valkey instance |
| Bloom Filter (`BF.*`, `MBbloom--`) | 🧩 Needs module | Requires the RedisBloom module on the target Valkey instance |
| Search indices (RediSearch / `FT.SEARCH`) | 🧩 Recreate indices | Aiven supports `FT.SEARCH` on Valkey 9+, but indices are not keys, so `DUMP`/`RESTORE` migrates the underlying hashes only — recreate the indices on the target |

**Legend:** ✅ migrates with no extra setup · 🧩 migrates only if the matching module is enabled (or the index is recreated) on the target.

Run the compatibility check below to see which of these apply to your data:

```bash
mise run check
```

## Quick Start (Using Docker)

The easiest way to run the migration tools without installing Python, `mise`, or `valkey-cli` locally is via Docker.

### 1. Configuration
By default, the tools will connect to a local Valkey/Redis instance at `valkey://localhost:6379`. If you are migrating real data, you will need to set up your remote source and target connection strings.

The dockerfile is looking for `SOURCE_CONNECTION_STRING` and `TARGET_CONNECTION_STRING`. Otherwise, it will assume that a local valkey instance (included in the image) is both the source and the target. You can provide them in when you build your Docker instance. Alternatively, you can supply the connection strings directly when running any of the commands.


### 2. Build and Run
1. **Build the Docker Image:**
   ```bash
   docker build \
     --build-arg SOURCE_CONNECTION_STRING="valkey://user:pass@source:6379" \
     --build-arg TARGET_CONNECTION_STRING="valkey://user:pass@target:6379" \
     -t vk-migrate .
   ```

2. **Run an Interactive Session:**
   Drop into a bash session inside the container.

   ```bash
   docker run -it vk-migrate bash
   ```

3. **Run Tasks inside the Container:**
   You can now execute `mise` tasks such as running checks or loading data:
   ```bash
   # Start the built-in Valkey server in the background (with modules loaded for testing)
   mise run start-server

   # Load a sample passing dataset and run the migration check
   mise run check-passing

   # Load a sample failing dataset and run the migration check
   mise run check-failing

   # Check if source data is compatible with Target (Valkey)
   mise run check

   # Run the migration check (compares Source and Target)
   mise run compare

   # List all available commands
   mise tasks
   ```

   Alternatively, you can use the CLI directly:
   ```bash
   uv run vk_migrate --help
   uv run vk_migrate migration-check
   ```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
