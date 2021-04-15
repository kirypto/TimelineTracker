import logging
from json import loads, dumps
from pathlib import Path
from typing import Dict, Any, List

from adapter.persistence.json_file_data_migrations import JsonDataMigrationScript
from adapter.views import JsonTranslator
from domain.events import Event
from domain.locations import Location


UTF8 = "utf8"


class DataMigration(JsonDataMigrationScript):
    def __init__(self, repository_root_path: Path) -> None:
        super().__init__(repository_root_path)

    def validate_safe_to_migrate(self) -> None:
        location_and_event_jsons: List[Dict[str, Any]] = []
        for location_json_file in filter(lambda x: x.suffix == ".json", self.location_repo_dir.iterdir()):
            location_and_event_jsons.append(loads(location_json_file.read_text("utf-8")))
        for event_json_file in filter(lambda x: x.suffix == ".json", self.event_repo_dir.iterdir()):
            location_and_event_jsons.append(loads(event_json_file.read_text("utf-8")))

        is_safe_to_migrate = True
        for json_object in location_and_event_jsons:
            reality_range = json_object["span"]["reality"]
            reality_range_width = abs(reality_range["high"] - reality_range["low"])
            if reality_range_width > 1000:
                logging.error(f"Object {json_object['id']} has a reality range larger than 1000 and needs to be migrated manually. "
                              f"(was {reality_range_width})")
                is_safe_to_migrate = False
        if not is_safe_to_migrate:
            raise ValueError(f"Migration to {self.get_migration_version_from_file(__file__)} would be unsafe, aborting. See log for detail")

    def _inner_migrate_data(self) -> None:
        for location_json_file in filter(lambda x: x.suffix == ".json", self.location_repo_dir.iterdir()):
            self._update_reality_to_be_integer_set(location_json_file, entity_type=Location)

        for event_json_file in filter(lambda x: x.suffix == ".json", self.event_repo_dir.iterdir()):
            self._update_reality_to_be_integer_set(event_json_file, entity_type=Event)

    @staticmethod
    def _update_reality_to_be_integer_set(json_file: Path, *, entity_type: Any) -> None:
        json_data = loads(json_file.read_text(UTF8))
        low = int(json_data["span"]["reality"]["low"])
        high = int(json_data["span"]["reality"]["high"])
        reality = [i for i in range(low, high + 1)]
        json_data["span"]["reality"] = reality
        entity = JsonTranslator.from_json(json_data, entity_type)
        json_file.write_text(dumps(JsonTranslator.to_json(entity), indent=2), UTF8)
