from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, anon_description, anon_tag
from usecase.locations_usecases import LocationUseCase


class TestLocationUsecase(TestCase):
    location_use_case: LocationUseCase

    def setUp(self) -> None:
        self.location_use_case = LocationUseCase()

    def test__create_location__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        location = self.location_use_case.create_location(span=anon_positional_range())

        # Assert
        self.assertTrue(hasattr(location, "id"))

    def test__create_location__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        location = self.location_use_case.create_location(id=undesired_id, span=anon_positional_range())

        # Assert
        self.assertNotEqual(undesired_id, location.id)

    def test__create_location__should_use_provided_args(self) -> None:
        # Arrange
        expected_span = anon_positional_range()
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}

        # Act
        location = self.location_use_case.create_location(span=expected_span, name=expected_name, description=expected_description,
                                                          tags=expected_tags)

        # Assert
        self.assertEqual(expected_span, location.span)
        self.assertEqual(expected_name, location.name)
        self.assertEqual(expected_description, location.description)
        self.assertEqual(expected_tags, location.tags)
