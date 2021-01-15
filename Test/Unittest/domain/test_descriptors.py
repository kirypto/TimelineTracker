from random import choices, choice
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_name, anon_description
from domain.base_entity import BaseEntity
from domain.descriptors import NamedEntity, DescribedEntity


# noinspection PyPropertyAccess,PyTypeChecker
class TestNamedEntity(TestCase):
    def test__init__should_reject_invalid_types(self) -> None:
        # Arrange
        invalid_type = choice([1.0, False, True])

        # Act
        def Action(): NamedEntity(name=invalid_type)

        # Assert
        self.assertRaises(TypeError, Action)

    def test__init__should_reject_invalid_characters(self) -> None:
        # Arrange
        invalid_name = anon_name(4) + "".join(choices("!@#$%^&*()+={}[]|\\:;"'<>,?/', k=1))

        # Act
        def Action(): _ = NamedEntity(name=invalid_name)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__init__should_reject_empty_string(self) -> None:
        # Arrange

        # Act
        def Action(): _ = NamedEntity(name="   ")

        # Assert
        self.assertRaises(ValueError, Action)

    def test__init__should_initialize_with_provided_value(self) -> None:
        # Arrange
        expected = anon_name()

        # Act
        actual = NamedEntity(name=expected)

        # Assert
        self.assertEqual(expected, actual.name)

    def test__init__should_accept_kwargs(self) -> None:
        # Arrange
        class TestKwargs(NamedEntity, _Other):
            pass

        # Act
        expected = "other"

        def Action(): return TestKwargs(name=anon_name(), other=expected)
        actual = Action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__name__should_not_be_mutable(self) -> None:
        # Arrange
        named_entity = NamedEntity(name=anon_name())

        # Act
        def Action(): named_entity.name = anon_name()

        # Assert
        self.assertRaises(AttributeError, Action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        name_1 = anon_name()
        name_2 = anon_name()
        named_entity_a = NamedEntity(name=name_1)
        named_entity_b = NamedEntity(name=name_1)
        named_entity_c = NamedEntity(name=name_2)

        # Act
        actual_a_equals_b = named_entity_a == named_entity_b
        actual_a_not_equals_b = named_entity_a != named_entity_b
        actual_a_equals_c = named_entity_a == named_entity_c
        actual_a_not_equals_c = named_entity_a != named_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        
    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        named_entity = NamedEntity(name=anon_name())

        # Act
        def Action(): _ = {named_entity}

        # Assert
        Action()


# noinspection PyPropertyAccess
class TestDescribedEntity(TestCase):
    def test__init__should_default_to_empty_string(self) -> None:
        # Arrange

        # Act
        actual = DescribedEntity()

        # Assert
        self.assertEqual("", actual.description)

    def test__init__should_initialize_with_provided_value(self) -> None:
        # Arrange
        expected = anon_description()

        # Act
        actual = DescribedEntity(description=expected)

        # Assert
        self.assertEqual(expected, actual.description)

    def test__init__should_accept_kwargs(self) -> None:
        # Arrange
        class TestKwargs(DescribedEntity, _Other):
            pass

        # Act
        expected = "other"

        def Action(): return TestKwargs(description=anon_description(), other=expected)
        actual = Action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__description__should_not_be_mutable(self) -> None:
        # Arrange
        described_entity = DescribedEntity(description=anon_description())

        # Act
        def Action(): described_entity.description = anon_description()

        # Assert
        self.assertRaises(AttributeError, Action)

    def test__equality__should_correctly_compare_tags(self) -> None:
        # Arrange
        description_1 = anon_description()
        description_2 = anon_description()
        described_entity_a = DescribedEntity(description=description_1)
        described_entity_b = DescribedEntity(description=description_1)
        described_entity_c = DescribedEntity(description=description_2)

        # Act
        actual_a_equals_b = described_entity_a == described_entity_b
        actual_a_not_equals_b = described_entity_a != described_entity_b
        actual_a_equals_c = described_entity_a == described_entity_c
        actual_a_not_equals_c = described_entity_a != described_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        named_entity = DescribedEntity(description=anon_description())

        # Act
        def Action(): _ = {named_entity}

        # Assert
        Action()


class _Other(BaseEntity):
    def __init__(self, *, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
