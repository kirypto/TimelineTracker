import logging
from json import loads
from pathlib import Path
from re import match
from typing import Dict, Any, List

from adapter.persistence.json_file_data_migrations import JsonDataMigrationScript


UTF8 = "utf8"


class DataMigration(JsonDataMigrationScript):
    @property
    def _file_name(self) -> str:
        return __file__

    def __init__(self, repository_root_path: Path) -> None:
        super().__init__(repository_root_path)

    def _is_safe_to_migrate(self) -> bool:
        metadata_entities: List[Dict[str, Any]] = []
        for location_json_file in filter(lambda x: x.suffix == ".json", self.location_repo_dir.iterdir()):
            metadata_entities.append(loads(location_json_file.read_text("utf-8")))
        for traveler_json_file in filter(lambda x: x.suffix == ".json", self.traveler_repo_dir.iterdir()):
            metadata_entities.append(loads(traveler_json_file.read_text("utf-8")))
        for event_json_file in filter(lambda x: x.suffix == ".json", self.event_repo_dir.iterdir()):
            metadata_entities.append(loads(event_json_file.read_text("utf-8")))

        is_safe_to_migrate = True
        for json_object in metadata_entities:
            metadata: Dict[str, str] = json_object["metadata"]
            for key, value in metadata.items():
                obj_id = json_object["id"]
                obj_type = obj_id.split("-")[0].capitalize()
                if not match(r"^[\w\-.]+$", key.strip()):
                    logging.error(f"{obj_type} {obj_id} has an illegal metadata key '{key}', must be non-empty with only alphanumeric, "
                                  f"dash, and decimal characters.")
                    is_safe_to_migrate = False
                if len(value.strip()) == 0:
                    logging.error(f"{obj_type} {obj_id} has an empty metadata value.")
                    is_safe_to_migrate = False
        return is_safe_to_migrate

    def _inner_migrate_data(self) -> None:
        pass
