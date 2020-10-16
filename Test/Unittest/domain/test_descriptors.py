from random import choices
from string import ascii_letters, printable
from unittest import TestCase

from domain.descriptors import NamedEntity, DescribedEntity


def anon_name(num_chars: int = 10) -> str:
    return "".join(choices(ascii_letters + "_ ", k=num_chars))


def anon_description(num_chars: int = 100) -> str:
    return "".join(choices(printable, k=num_chars))


class TestNamedEntity(TestCase):
    def test__init__should_reject_illegal_characters(self) -> None:
        # Arrange
        illegal_name = anon_name(4) + "".join(choices("!@#$%^&*()+={}[]|\\:;"'<>,.?/', k=1))

        # Act
        def Action(): _ = NamedEntity(name=illegal_name)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__init__should_default_to_empty_string(self) -> None:
        # Arrange

        # Act
        actual = NamedEntity()

        # Assert
        self.assertEqual("", actual.name)

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


class _Other:
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
