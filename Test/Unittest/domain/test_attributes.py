from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_attribute_key, anon_attribute_value, anon_attributes, anon_anything, anon_description
from domain.attributes import AttributedEntity
from domain.base_entity import BaseEntity


class TestAttributedEntity(TestCase):
    def test__init__should_initialize_empty__when_no_attributed_given(self) -> None:
        # Arrange
        attributed_entity = AttributedEntity()

        # Act
        actual = attributed_entity.attributes

        # Assert
        self.assertDictEqual({}, actual)

    def test__init__should_initialize_attributed__when_attributed_given(self) -> None:
        # Arrange
        expected = anon_attributes()
        attributed_entity = AttributedEntity(attributes=expected)

        # Act
        actual = attributed_entity.attributes

        # Assert
        self.assertDictEqual(expected, actual)

    def test__init__should_strip_attributed_whitespace__when_attributed_keys_or_values_have_whitespace(self) -> None:
        # Arrange
        attributed_key = anon_attribute_key()
        attributed_value = anon_attribute_value()
        expected = {attributed_key: attributed_value}
        attributed_entity = AttributedEntity(attributes={f" {attributed_key}\t": f"\n{attributed_value}\t"})

        # Act
        actual = attributed_entity.attributes

        # Assert
        self.assertDictEqual(expected, actual)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class TestKwargs(AttributedEntity, _Other):
            pass

        # Act
        expected = "other"

        def action(): return TestKwargs(attributes=anon_attributes(), other=expected)

        actual = action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange

        # Act
        def action(): AttributedEntity(attributes=anon_anything(not_type=dict))

        # Assert
        self.assertRaises(TypeError, action)

    def test__init__should_reject_empty_key(self) -> None:
        # Arrange
        value = anon_attribute_value()

        # Act
        def action(): AttributedEntity(attributes={"": value})

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_reject_empty_value(self) -> None:
        # Arrange
        key = anon_attribute_key()

        # Act
        def action(): AttributedEntity(attributes={key: ""})

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_reject_attributed_keys_of_invalid_type(self) -> None:
        # Arrange
        attributed = {anon_anything(not_type=str): anon_attribute_value()}

        # Act
        def action(): AttributedEntity(attributes=attributed)

        # Assert
        self.assertRaises(TypeError, action)

    def test__init__should_reject_attributed_keys_with_invalid_chars(self) -> None:
        # Arrange
        attributed = {anon_description(): anon_attribute_value()}

        # Act
        def action(): AttributedEntity(attributes=attributed)

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_reject_attributed_values_of_invalid_type(self) -> None:
        # Arrange
        attributed = {anon_attribute_key(): anon_anything(not_type=str)}

        # Act
        def action(): AttributedEntity(attributes=attributed)

        # Assert
        self.assertRaises(TypeError, action)

    def test__attributes__should_not_allow_external_mutation(self) -> None:
        # Arrange
        expected = anon_attributes()
        attributed_entity = AttributedEntity(attributes=expected)
        attributed = attributed_entity.attributes

        # Act
        attributed[anon_attribute_key()] = anon_attribute_value()

        # Assert
        self.assertDictEqual(expected, attributed_entity.attributes)

    def test__attributes__should_not_be_settable(self) -> None:
        # Arrange
        attributed_entity = AttributedEntity()

        # Act
        # noinspection PyPropertyAccess
        def action(): attributed_entity.attributes = anon_attributes()

        # Assert
        self.assertRaises(AttributeError, action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        attributes_dict_1 = anon_attributes()
        attributes_dict_2 = anon_attributes()
        attributed_entity_a = AttributedEntity(attributes=attributes_dict_1)
        attributed_entity_b = AttributedEntity(attributes=attributes_dict_1)
        attributed_entity_c = AttributedEntity(attributes=attributes_dict_2)

        # Act
        actual_a_equals_b = attributed_entity_a == attributed_entity_b
        actual_a_not_equals_b = attributed_entity_a != attributed_entity_b
        actual_a_equals_c = attributed_entity_a == attributed_entity_c
        actual_a_not_equals_c = attributed_entity_a != attributed_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable__when_has_no_attributed(self) -> None:
        # Arrange
        attributed_entity = AttributedEntity()

        # Act
        def action(): _ = {attributed_entity}

        # Assert
        action()

    def test__hash__should_be_hashable__when_has_attributed(self) -> None:
        # Arrange
        attributed_entity = AttributedEntity(attributes=anon_attributes())

        # Act
        def action(): _ = {attributed_entity}

        # Assert
        action()


class _Other(BaseEntity):
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
