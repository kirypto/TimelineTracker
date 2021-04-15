from pathlib import Path

from adapter.persistence.json_file_data_migrations import JsonDataMigrationScript


UTF8 = "utf8"


# Nothing to do, just bump Json data version
class DataMigration(JsonDataMigrationScript):
    def __init__(self, repository_root_path: Path) -> None:
        super().__init__(repository_root_path)

    @property
    def _file_name(self) -> str:
        return __file__

    def _is_safe_to_migrate(self) -> bool:
        return True

    def _inner_migrate_data(self) -> None:
        pass
