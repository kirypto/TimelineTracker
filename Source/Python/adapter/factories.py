from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository
from adapter.persistence.json_file_repositories import JsonFileLocationRepository, JsonFileTravelerRepository
from domain.persistence.repositories import TravelerRepository, LocationRepository


class RepositoriesFactory:
    _traveler_repo: TravelerRepository
    _location_repo: LocationRepository

    @property
    def location_repo(self) -> LocationRepository:
        return self._location_repo

    @property
    def traveler_repo(self) -> TravelerRepository:
        return self._traveler_repo

    def __init__(self, repository_type: str, **kwargs) -> None:
        if repository_type == "json":
            self._location_repo = JsonFileLocationRepository(**kwargs)
            self._traveler_repo = JsonFileTravelerRepository(**kwargs)
        elif repository_type == "memory":
            self._location_repo = InMemoryLocationRepository()
            self._traveler_repo = InMemoryTravelerRepository()
        else:
            raise ValueError(f"Unsupported repository type {repository_type}")
