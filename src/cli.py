import click

from .compatibility_check import compatibility_check_cmd
from .examine import examine_cmd
from .flush import flush_cmd
from .flush_all import flush_all_cmd
from .load_fake_data import load_fake_data_cmd
from .migrate_data import migrate_data_cmd
from .migration_check import migration_check_cmd

@click.group()
def cli():
    """Tools and instructions to migrate between Redis-compatible databases (e.g., Dragonfly/Redis to Valkey)"""
    pass

cli.add_command(compatibility_check_cmd, name="compatibility-check")
cli.add_command(examine_cmd, name="examine")
cli.add_command(flush_cmd, name="flush")
cli.add_command(flush_all_cmd, name="flush-all")
cli.add_command(load_fake_data_cmd, name="load-fake-data")
cli.add_command(migrate_data_cmd, name="migrate-data")
cli.add_command(migration_check_cmd, name="migration-check")

if __name__ == "__main__":
    cli()
