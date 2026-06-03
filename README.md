# Dragonfly to Valkey Migration Project

This project contains tools and instructions to help migrate data from Aiven for Dragonfly to Aiven for Valkey.

## Quick Start (Using Docker)

The easiest way to run the migration tools without installing Python, `mise`, or `valkey-cli` locally is via Docker.

### 1. Configuration
By default, the tools will connect to a local Valkey/Redis instance at `valkey://localhost:6379`. If you are migrating real data, you will need to set up your remote source and target connection strings. We use `fnox` to manage these securely.

1. Copy the example configuration file:
   ```bash
   cp fnox.toml.example fnox.toml
   ```
2. Edit `fnox.toml` and configure your target and source connection strings. This file uses the `plaintext` provider by default for local development. *(Note: `fnox.toml` is and should remain in your `.gitignore` to prevent committing secrets).*

3. If you have an existing `.env` file or wish to set values interactively, you can import them using the `fnox` CLI. For detailed instructions on importing and managing secrets, refer to the [fnox documentation](https://fnox.jdx.dev/).

### 2. Build and Run
1. **Build the Docker Image:**
   ```bash
   docker build -t vk-migrate .
   ```

2. **Run an Interactive Session:**
   Drop into a bash session inside the container, mounting your `fnox` config:
   ```bash
   docker run -it -v $(pwd)/fnox.toml:/app/fnox.toml vk-migrate fnox exec -- bash
   ```
   *(Note: If you just want to test locally and don't care about `fnox.toml`, you can simply run `docker run -it vk-migrate bash`)*

3. **Run Tasks inside the Container:**
   You can now execute `mise` tasks such as running checks or loading data:
   ```bash
   # Start the built-in Valkey server in the background (optional, for testing without external databases)
   valkey-server --daemonize yes

   # Load a sample passing dataset and run the migration check
   mise run check-passing

   # Load a sample failing dataset and run the migration check
   mise run check-failing

   # Check if source data is compatible with Valkey
   mise run check

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
