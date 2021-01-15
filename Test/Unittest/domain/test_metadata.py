from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_metadata_key, anon_metadata_value, anon_metadata, anon_anything, anon_description
from domain.base_entity import BaseEntity
from domain.metadata import MetadataEntity


class TestMetadataEntity(TestCase):
    def test__init__should_initialize_empty__when_no_metadata_given(self) -> None:
        # Arrange
        metadata_entity = MetadataEntity()

        # Act
        actual = metadata_entity.metadata

        # Assert
        self.assertDictEqual({}, actual)

    def test__init__should_initialize_metadata__when_metadata_given(self) -> None:
        # Arrange
        expected = anon_metadata()
        metadata_entity = MetadataEntity(metadata=expected)

        # Act
        actual = metadata_entity.metadata

        # Assert
        self.assertDictEqual(expected, actual)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class TestKwargs(MetadataEntity, _Other):
            pass

        # Act
        expected = "other"

        def action(): return TestKwargs(metadata=anon_metadata(), other=expected)

        actual = action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange

        # Act
        def action(): MetadataEntity(metadata=anon_anything(not_type=dict))

        # Assert
        self.assertRaises(TypeError, action)

    def test__init__should_reject_metadata_keys_of_invalid_type(self) -> None:
        # Arrange
        metadata = {anon_anything(not_type=str): anon_metadata_value()}

        # Act
        def action(): MetadataEntity(metadata=metadata)

        # Assert
        self.assertRaises(TypeError, action)

    def test__init__should_reject_metadata_keys_with_invalid_chars(self) -> None:
        # Arrange
        metadata = {anon_description(): anon_metadata_value()}

        # Act
        def action(): MetadataEntity(metadata=metadata)

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_reject_metadata_values_of_invalid_type(self) -> None:
        # Arrange
        metadata = {anon_metadata_key(): anon_anything(not_type=str)}

        # Act
        def action(): MetadataEntity(metadata=metadata)

        # Assert
        self.assertRaises(TypeError, action)

    def test__metadata__should_not_allow_external_mutation(self) -> None:
        # Arrange
        expected = anon_metadata()
        metadata_entity = MetadataEntity(metadata=expected)
        metadata = metadata_entity.metadata

        # Act
        metadata[anon_metadata_key()] = anon_metadata_value()

        # Assert
        self.assertDictEqual(expected, metadata_entity.metadata)

    def test__metadata__should_not_be_settable(self) -> None:
        # Arrange
        metadata_entity = MetadataEntity()

        # Act
        # noinspection PyPropertyAccess
        def action(): metadata_entity.metadata = anon_metadata()

        # Assert
        self.assertRaises(AttributeError, action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        metadata_dict_1 = anon_metadata()
        metadata_dict_2 = anon_metadata()
        metadata_entity_a = MetadataEntity(metadata=metadata_dict_1)
        metadata_entity_b = MetadataEntity(metadata=metadata_dict_1)
        metadata_entity_c = MetadataEntity(metadata=metadata_dict_2)

        # Act
        actual_a_equals_b = metadata_entity_a == metadata_entity_b
        actual_a_not_equals_b = metadata_entity_a != metadata_entity_b
        actual_a_equals_c = metadata_entity_a == metadata_entity_c
        actual_a_not_equals_c = metadata_entity_a != metadata_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable__when_has_no_metadata(self) -> None:
        # Arrange
        metadata_entity = MetadataEntity()

        # Act
        def action(): _ = {metadata_entity}

        # Assert
        action()

    def test__hash__should_be_hashable__when_has_metadata(self) -> None:
        # Arrange
        metadata_entity = MetadataEntity(metadata=anon_metadata())

        # Act
        def action(): _ = {metadata_entity}

        # Assert
        action()


class _Other(BaseEntity):
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
