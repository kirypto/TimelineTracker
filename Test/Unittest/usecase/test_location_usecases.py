from random import choice
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_prefixed_id, anon_positional_range, anon_name, anon_description, anon_tag, \
    anon_create_location_kwargs
from adapter.persistence.in_memory_repositories import InMemoryLocationRepository
from usecase.locations_usecases import LocationUseCase


class TestLocationUsecase(TestCase):
    location_use_case: LocationUseCase

    def setUp(self) -> None:
        self.location_use_case = LocationUseCase(InMemoryLocationRepository())

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

    def test__retrieve__should_return_saved__when_exists(self) -> None:
        # Arrange
        expected = self.location_use_case.create(**anon_create_location_kwargs())

        # Act
        actual = self.location_use_case.retrieve(expected.id)

        # Assert
        self.assertEqual(expected, actual)

    def test__retrieve__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.location_use_case.retrieve(anon_prefixed_id(prefix="location"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__retrieve_all__should_return_all_saved__when_no_filters_provided(self) -> None:
        # Arrange
        location_a = self.location_use_case.create(**anon_create_location_kwargs())
        location_b = self.location_use_case.create(**anon_create_location_kwargs())
        expected = {location_a, location_b}

        # Act
        actual = self.location_use_case.retrieve_all()

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_matching_filters__when_name_filter_provided(self) -> None:
        # Arrange
        name = anon_name()
        location_a_kwargs = anon_create_location_kwargs(name=name)
        location_b_kwargs = anon_create_location_kwargs(name=name)
        location_a = self.location_use_case.create(**location_a_kwargs)
        location_b = self.location_use_case.create(**location_b_kwargs)
        expected = {location_a, location_b}

        # Act
        actual = self.location_use_case.retrieve_all(name=name)

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_matching_filters__when_tagged_with_all_filter_provided(self) -> None:
        # Arrange
        query_tag_1 = anon_tag()
        query_tag_2 = anon_tag()
        other_tag = anon_tag()
        location_with_additional = self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2, other_tag}))
        location_with_all_queried = self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2}))
        self.location_use_case.create(**anon_create_location_kwargs(tags={choice([query_tag_1, query_tag_2])}))  # location with only one
        self.location_use_case.create(**anon_create_location_kwargs(tags={other_tag}))  # location with other tag
        self.location_use_case.create(**anon_create_location_kwargs(tags=set()))  # location without any tags
        expected = {location_with_additional, location_with_all_queried}

        # Act
        actual = self.location_use_case.retrieve_all(tagged_with_all={query_tag_1, query_tag_2})

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_matching_filters__when_tagged_with_any_filter_provided(self) -> None:
        # Arrange
        query_tag_1 = anon_tag()
        query_tag_2 = anon_tag()
        other_tag = anon_tag()
        location_with_additional = self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2, other_tag}))
        location_with_all_queried = self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2}))
        location_with_only_one = self.location_use_case.create(**anon_create_location_kwargs(tags={choice([query_tag_1, query_tag_2])}))
        self.location_use_case.create(**anon_create_location_kwargs(tags={other_tag}))  # location with other tag
        self.location_use_case.create(**anon_create_location_kwargs(tags=set()))  # location without any tags
        expected = {location_with_additional, location_with_all_queried, location_with_only_one}

        # Act
        actual = self.location_use_case.retrieve_all(tagged_with_any={query_tag_1, query_tag_2})

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_matching_filters__when_tagged_with_only_filter_provided(self) -> None:
        # Arrange
        query_tag_1 = anon_tag()
        query_tag_2 = anon_tag()
        other_tag = anon_tag()
        self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2, other_tag}))  # location with additional
        location_with_all_queried = self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2}))
        location_with_only_one = self.location_use_case.create(**anon_create_location_kwargs(tags={choice([query_tag_1, query_tag_2])}))
        self.location_use_case.create(**anon_create_location_kwargs(tags={other_tag}))  # location with other tag
        location_without_tags = self.location_use_case.create(**anon_create_location_kwargs(tags=set()))
        expected = {location_with_all_queried, location_with_only_one, location_without_tags}

        # Act
        actual = self.location_use_case.retrieve_all(tagged_with_only={query_tag_1, query_tag_2})

        # Assert
        self.assertSetEqual(expected, actual)

    def test__retrieve_all__should_return_all_matching_filters__when_tagged_with_none_filter_provided(self) -> None:
        # Arrange
        query_tag_1 = anon_tag()
        query_tag_2 = anon_tag()
        other_tag = anon_tag()
        self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2, other_tag}))  # location with additional
        self.location_use_case.create(**anon_create_location_kwargs(tags={query_tag_1, query_tag_2}))  # location with all queried
        self.location_use_case.create(**anon_create_location_kwargs(tags={choice([query_tag_1, query_tag_2])}))  # location with only one
        location_with_other_tag = self.location_use_case.create(**anon_create_location_kwargs(tags={other_tag}))
        location_without_tags = self.location_use_case.create(**anon_create_location_kwargs(tags=set()))
        expected = {location_with_other_tag, location_without_tags}

        # Act
        actual = self.location_use_case.retrieve_all(tagged_with_none={query_tag_1, query_tag_2})

        # Assert
        self.assertSetEqual(expected, actual)
        
    def test__delete__should_delete__when_location_exists(self) -> None:
        # Arrange
        location = self.location_use_case.create(**anon_create_location_kwargs())

        # Act
        self.location_use_case.delete(location.id)
        
        # Assert
        self.assertRaises(NameError, lambda: self.location_use_case.retrieve(location.id))

    def test__delete__should_raise_exception__when_not_exits(self) -> None:
        # Arrange

        # Act
        def Action(): self.location_use_case.delete(anon_prefixed_id(prefix="location"))

        # Assert
        self.assertRaises(NameError, Action)

    def test__update__should_raise_exception__when_not_exists(self) -> None:
        # Arrange

        # Act
        def Action(): self.location_use_case.update(anon_prefixed_id(prefix="location"), name=anon_name())

        # Assert
        self.assertRaises(NameError, Action)
        
    def test__update__should_reject_attempts_to_change_id(self) -> None:
        # Arrange
        location = self.location_use_case.create(**anon_create_location_kwargs())

        # Act
        # noinspection PyArgumentList
        def Action(): self.location_use_case.update(location.id, id=anon_prefixed_id(prefix="location"))

        # Assert
        self.assertRaises(TypeError, Action)

    def test__update__should_update_provided_attributes__when_attributes_provided(self) -> None:
        # Arrange
        location = self.location_use_case.create(**anon_create_location_kwargs())
        expected_name = anon_name()
        expected_description = anon_description()
        expected_span = anon_positional_range()
        expected_tags = {anon_tag(), anon_tag()}

        # Act
        actual_updated_name = self.location_use_case.update(location.id, name=expected_name)
        actual_updated_description = self.location_use_case.update(location.id, description=expected_description)
        actual_updated_span = self.location_use_case.update(location.id, span=expected_span)
        actual_updated_tags = self.location_use_case.update(location.id, tags=expected_tags)

        # Assert
        self.assertEqual(expected_name, actual_updated_name.name)
        self.assertEqual(expected_description, actual_updated_description.description)
        self.assertEqual(expected_span, actual_updated_span.span)
        self.assertEqual(expected_tags, actual_updated_tags.tags)
