# Dragonfly to Valkey Migration Project

This project contains tools and instructions to help migrate data from Aiven for Dragonfly to Aiven for Valkey. 

## Quick Start (Using Docker)

The easiest way to run the migration tools without installing Python, `mise`, or `valkey-cli` locally is via Docker.

1. **Build the Docker Image:**
   ```bash
   docker build -t df-valkey-migration .
   ```

2. **Run an Interactive Session:**
   Drop into a bash session inside the container, mounting your `fnox` config so that connection strings can be decrypted:
   ```bash
   docker run -it -v ~/.config/fnox:/root/.config/fnox df-valkey-migration bash
   ```

3. **Run Tasks inside the Container:**
   You can now execute `mise` tasks such as running checks or loading data:
   ```bash
   mise run check
   mise run load-passing
   mise run check-passing
   ```

---

## Migration Steps

If you are performing a full migration, you can follow these general steps using `valkey-cli` directly.

### Prerequisites
- A running Aiven for Valkey target service.
- A running Aiven for Dragonfly source service.
- Connection details for both services.

### Compatibility Considerations
- Review the [Dragonfly command compatibility list](https://www.dragonflydb.io/docs/command-reference/compatibility).
- **Aiven for Valkey supports the JSON module natively**, but it does not support some other extensions (like Search or TimeSeries). Ensure your target Valkey service has equivalent capabilities or plan a transformation step.
- Always test your application against Valkey in a staging environment.

### Step 1: Extract Data
You can create a full RDB snapshot of your Dragonfly service using `valkey-cli`.

1. **Trigger a Background Save:**
   ```bash
   valkey-cli -h <dragonfly-host> -p <dragonfly-port> \
     --tls --no-auth-warning \
     -a <dragonfly-password> \
     BGSAVE
   ```
2. **Wait for the Save to Complete:**
   Check the last save timestamp to ensure it has updated:
   ```bash
   valkey-cli -h <dragonfly-host> -p <dragonfly-port> \
     --tls --no-auth-warning \
     -a <dragonfly-password> \
     LASTSAVE
   ```
3. **Download the Snapshot:**
   ```bash
   valkey-cli -h <dragonfly-host> -p <dragonfly-port> \
     --tls --no-auth-warning \
     -a <dragonfly-password> \
     --rdb dragonfly-dump.rdb
   ```
   This produces a `dragonfly-dump.rdb` file in your current directory.