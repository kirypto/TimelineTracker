from typing import Set, Any, TypeVar, Type, List, Dict
from unittest import TestCase

from parameterized import parameterized

from application.requests.data_forms import JsonTranslator
from domain.collections import Range
from domain.events import Event
from domain.ids import PrefixedUUID
from domain.locations import Location
from domain.positions import PositionalRange, PositionalMove, Position, MovementType
from domain.tags import Tag
from domain.travelers import Traveler
from domain.worlds import World
from test_helpers.anons import anon_anything


T = TypeVar("T")


class JsonTranslatorTest(TestCase):
    @parameterized.expand([
        (Set[Tag], anon_anything(not_type=list)),
        (Set[Tag], "raw_string"),
        (Set[Tag], {"key": "value"}),
        (str, anon_anything(not_type=str)),
        (Set[PrefixedUUID], anon_anything(not_type=list)),
        (PrefixedUUID, anon_anything(not_type=str)),
        (PositionalRange, anon_anything(not_type=dict)),
        (Range[float], anon_anything(not_types={dict, float, int})),
        (Set[Tag], anon_anything(not_type=list)),
        (Tag, anon_anything(not_type=str)),
        (List[PositionalMove], anon_anything(not_type=list)),
        (PositionalMove, anon_anything(not_type=dict)),
        (Position, anon_anything(not_type=dict)),
        (MovementType, anon_anything(not_type=str)),
        (Dict[str, str], anon_anything(not_type=dict)),
        (World, anon_anything(not_type=dict)),
        (Location, anon_anything(not_type=dict)),
        (Traveler, anon_anything(not_type=dict)),
        (Event, anon_anything(not_type=dict)),
        (Set[int], anon_anything(not_types={list, float, int})),
    ])
    def test__from_json__should_reject__when_params_invalid(
            self, type_: Type[T], invalid_param: Any
    ) -> None:
        # Arrange
        # Act
        def action(): JsonTranslator.from_json(invalid_param, type_)

        # Assert
        with self.assertRaises(TypeError) as _:
            action()
            self.fail(f"Should not have been able to parse a {type_} from '{invalid_param}'")
