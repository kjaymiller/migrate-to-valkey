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
2. Edit `fnox.toml` and configure your `age` public key if you intend to use `age` encryption. If you prefer to store connection strings locally without encryption, you can change the provider type to `plaintext` in the file.

3. Load your environment variables into `fnox`. If you have a `.env` file containing your connection strings:
   ```env
   SOURCE_CONNECTION_STRING=valkey://...
   TARGET_CONNECTION_STRING=valkey://...
   ```
   You can import them directly into `fnox`:
   ```bash
   fnox import --provider age --input .env
   ```
   *(Note: change `--provider age` to `--provider plaintext` if you updated your config in step 2)*

   Alternatively, you can set them one-by-one interactively, which will prompt you for the values without echoing them:
   ```bash
   fnox set SOURCE_CONNECTION_STRING
   fnox set TARGET_CONNECTION_STRING
   ```

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

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
