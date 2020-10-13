from random import choices
from string import ascii_letters, digits
from unittest import TestCase

from domain.tags import Tag, Tags


def anon_tag_name(num_digits: int = 10) -> str:
    return "".join(choices(ascii_letters + digits + "-_", k=num_digits))


def anon_tag() -> Tag:
    return Tag(anon_tag_name())


class TestTag(TestCase):
    def test__str__should_return_tag_as_plain_text(self) -> None:
        # Arrange
        expected = anon_tag_name()
        tag = Tag(expected)

        # Act
        actual = str(tag)

        # Assert
        self.assertEqual(expected, actual)

    def test__init__should_reject_illegal_characters(self) -> None:
        # Arrange
        illegal_tag = anon_tag_name(4) + "".join(choices("!@#$%^&*()+={}[]|\\:;"'<>,.?/', k=1))

        # Act
        def Action(): return Tag(illegal_tag)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__init__should_empty(self) -> None:
        # Arrange

        # Act
        def Action(): return Tag("")

        # Assert
        self.assertRaises(ValueError, Action)

    def test__equality__should_correctly_compare_tags(self) -> None:
        # Arrange
        tag_name_1 = anon_tag_name()
        tag_name_2 = anon_tag_name()
        tag_a = Tag(tag_name_1)
        tag_b = Tag(tag_name_1)
        tag_c = Tag(tag_name_2)

        # Act
        actual_a_equals_b = tag_a == tag_b
        actual_a_not_equals_b = tag_a != tag_b
        actual_a_equals_c = tag_a == tag_c
        actual_a_not_equals_c = tag_a != tag_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        tag = anon_tag()

        # Act
        def Action(): var = {tag}

        # Assert
        Action()


class TestTags(TestCase):
    def test__tags__should_initialize_empty(self) -> None:
        # Arrange
        tags = Tags()

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(set(), actual)

    def test__tags__should_not_allow_external_mutation(self) -> None:
        # Arrange
        tags = Tags()
        tag_set = tags.tags
        tag_set.add(anon_tag())

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(set(), actual)

    def test__add_tag__should_add_to_set(self) -> None:
        # Arrange
        tags = Tags()
        tag = anon_tag()
        tags.add_tag(tag)
        expected = {tag}

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(expected, actual)

    def test__add_tag__should_ignore_duplicates(self) -> None:
        # Arrange
        tags = Tags()
        tag = anon_tag()
        tags.add_tag(tag)
        tags.add_tag(tag)
        expected = {tag}

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(expected, actual)
    
    def test__remove_tag__should_remove_existent_tags(self) -> None:
        # Arrange
        tags = Tags()
        tags.add_tag(anon_tag())
        expected = tags.tags
        tag = anon_tag()
        tags.add_tag(tag)

        # Act
        tags.remove_tag(tag)

        # Assert
        actual = tags.tags
        self.assertSetEqual(expected, actual)

    def test__remove_tag__should_reject_non_existent_tags(self) -> None:
        # Arrange
        tags = Tags()

        # Act
        def Action(): tags.remove_tag(anon_tag())

        # Assert
        self.assertRaises(KeyError, Action)
