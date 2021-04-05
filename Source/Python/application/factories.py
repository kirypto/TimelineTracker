from importlib import import_module

from domain.persistence.repositories import TravelerRepository, LocationRepository, EventRepository


class RepositoriesFactory:
    _REPO_TYPES = {
        "memory": "in_memory_repositories",
        "json": "json_file_repositories",
    }
    _location_repo: LocationRepository
    _traveler_repo: TravelerRepository
    _event_repo: EventRepository

    @property
    def location_repo(self) -> LocationRepository:
        return self._location_repo

    @property
    def traveler_repo(self) -> TravelerRepository:
        return self._traveler_repo

    @property
    def event_repo(self) -> EventRepository:
        return self._event_repo

    def __init__(self, repository_type: str, **kwargs) -> None:
        if repository_type not in RepositoriesFactory._REPO_TYPES:
            raise ValueError(f"Unsupported repository type {repository_type}. "
                             f"Supported types are: {set(RepositoriesFactory._REPO_TYPES.keys())}")

        repositories_module = import_module(f"adapter.persistence.{RepositoriesFactory._REPO_TYPES[repository_type]}")
        location_repository_class = getattr(repositories_module, 'location_repository_class')
        traveler_repository_class = getattr(repositories_module, 'traveler_repository_class')
        event_repository_class = getattr(repositories_module, 'event_repository_class')

        self._location_repo = location_repository_class(**kwargs)
        self._traveler_repo = traveler_repository_class(**kwargs)
        self._event_repo = event_repository_class(**kwargs)
