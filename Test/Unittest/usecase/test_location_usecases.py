from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, anon_description, anon_tag, \
    anon_create_location_kwargs
from usecase.locations_usecases import LocationUseCase


class TestLocationUsecase(TestCase):
    location_use_case: LocationUseCase

    def setUp(self) -> None:
        self.location_use_case = LocationUseCase()

    def test__create__should_not_require_id_passed_in(self) -> None:
        # Arrange

        # Act
        location = self.location_use_case.create(span=anon_positional_range())

        # Assert
        self.assertTrue(hasattr(location, "id"))

    def test__create__should_ignore_id_if_provided(self) -> None:
        # Arrange
        undesired_id = anon_prefixed_id()

        # Act
        location = self.location_use_case.create(id=undesired_id, span=anon_positional_range())

        # Assert
        self.assertNotEqual(undesired_id, location.id)

    def test__create__should_use_provided_args(self) -> None:
        # Arrange
        expected_span = anon_positional_range()
        expected_name = anon_name()
        expected_description = anon_description()
        expected_tags = {anon_tag()}

        # Act
        location = self.location_use_case.create(span=expected_span, name=expected_name, description=expected_description,
                                                 tags=expected_tags)

        # Assert
        self.assertEqual(expected_span, location.span)
        self.assertEqual(expected_name, location.name)
        self.assertEqual(expected_description, location.description)
        self.assertEqual(expected_tags, location.tags)

    def test__retrieve__should_return_saved(self) -> None:
        # Arrange
        expected = self.location_use_case.create(**anon_create_location_kwargs())

        # Act
        actual = self.location_use_case.retrieve(expected.id)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve_all__should_return_all_saved(self) -> None:
        # Arrange
        location_a = self.location_use_case.create(**anon_create_location_kwargs())
        location_b = self.location_use_case.create(**anon_create_location_kwargs())
        expected = {location_a, location_b}

        # Act
        actual = self.location_use_case.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)
