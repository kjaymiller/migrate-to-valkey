# Dragonfly to Valkey Migration Project

This project contains tools and instructions to help migrate data from Aiven for Dragonfly to Aiven for Valkey.

## Quick Start (Using Docker)

The easiest way to run the migration tools without installing Python, `mise`, or `valkey-cli` locally is via Docker.

### 1. Configuration
Before running the container, you need to set up your source and target connection strings. We use `fnox` to manage these securely. 

1. Copy the example configuration file:
   ```bash
   cp fnox.toml.example fnox.toml
   ```
2. Edit `fnox.toml` and add your connection strings (and optionally, configure `age` encryption if desired).

### 2. Build and Run
1. **Build the Docker Image:**
   ```bash
   docker build -t df-valkey-migration .
   ```

2. **Run an Interactive Session:**
   Drop into a bash session inside the container, mounting your `fnox` config:
   ```bash
   docker run -it -v $(pwd)/fnox.toml:/app/fnox.toml df-valkey-migration bash
   ```

3. **Run Tasks inside the Container:**
   You can now execute `mise` tasks such as running checks or loading data:
   ```bash
   # Check if source data is compatible with Valkey
   mise run check
   
   # Load a sample passing dataset into the source
   mise run load-passing
   
   # Compare the data between source and target
   mise run compare
   
   # List all available commands
   mise tasks
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

---

## Contributing

We welcome contributions! If you'd like to help improve these migration tools, follow these steps to set up your local development environment.

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (for fast Python package management)
- [mise](https://mise.jdx.dev/) (for task running and environment management)
- Python 3.14+

### Local Setup
1. Clone the repository and navigate into it.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Copy the configuration template and configure your connection strings:
   ```bash
   cp fnox.toml.example fnox.toml
   ```

### Running Tests
We use standard Python unit tests located in the `tests/` directory.

To run the test suite, use `uv`:
```bash
uv run pytest
```

You can also use the `mise` tasks defined in `mise.toml` to interactively run checks and data loading against your configured test databases. Use `mise tasks` to see all available commands.