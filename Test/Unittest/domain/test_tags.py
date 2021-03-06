from random import choices
from unittest import TestCase

from Test.Unittest.test_helpers.anons import anon_tag_name, anon_tag
from domain.base_entity import BaseEntity
from domain.tags import Tag, TaggedEntity


# noinspection DuplicatedCode
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
        def action(): return Tag(illegal_tag)

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_reject_empty(self) -> None:
        # Arrange

        # Act
        def action(): return Tag("")

        # Assert
        self.assertRaises(ValueError, action)

    def test__init__should_strip_whitespace(self) -> None:
        # Arrange
        expected = anon_tag_name()
        tag = Tag(f" {expected}\t")

        # Act
        actual = str(tag)

        # Assert
        self.assertEqual(expected, actual)

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
        def action(): _ = {tag}

        # Assert
        action()


class TestTaggedEntity(TestCase):
    def test__init__should_initialize_empty__when_no_tags_given(self) -> None:
        # Arrange
        tags = TaggedEntity()

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(set(), actual)

    def test__init__should_initialize_tags__when_tags_given(self) -> None:
        # Arrange
        expected = {anon_tag(), anon_tag()}
        tags = TaggedEntity(tags=expected)

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(expected, actual)

    def test__init__should_support_kwargs(self) -> None:
        # Arrange
        class TestKwargs(TaggedEntity, _Other):
            pass

        # Act
        expected = "other"

        def action(): return TestKwargs(tags={anon_tag()}, other=expected)
        actual = action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__tags__should_not_allow_external_mutation(self) -> None:
        # Arrange
        tags = TaggedEntity()
        tag_set = tags.tags
        tag_set.add(anon_tag())

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(set(), actual)

    def test__tags__should_not_be_settable(self) -> None:
        # Arrange
        tags = TaggedEntity()

        # Act
        # noinspection PyPropertyAccess
        def action(): tags.tags = {anon_tag()}

        # Assert
        self.assertRaises(AttributeError, action)

    def test__add_tag__should_add_to_set(self) -> None:
        # Arrange
        tags = TaggedEntity()
        tag = anon_tag()
        tags.add_tag(tag)
        expected = {tag}

        # Act
        actual = tags.tags

        # Assert
        self.assertSetEqual(expected, actual)

    def test__add_tag__should_ignore_duplicates(self) -> None:
        # Arrange
        tags = TaggedEntity()
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
        tags = TaggedEntity()
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
        tags = TaggedEntity()

        # Act
        def action(): tags.remove_tag(anon_tag())

        # Assert
        self.assertRaises(KeyError, action)

    def test__equality__should_correctly_compare_attributes(self) -> None:
        # Arrange
        tag_set_1 = {anon_tag(), anon_tag()}
        tag_set_2 = {anon_tag(), anon_tag()}
        tagged_entity_a = TaggedEntity(tags=tag_set_1)
        tagged_entity_b = TaggedEntity(tags=tag_set_1)
        tagged_entity_c = TaggedEntity(tags=tag_set_2)

        # Act
        actual_a_equals_b = tagged_entity_a == tagged_entity_b
        actual_a_not_equals_b = tagged_entity_a != tagged_entity_b
        actual_a_equals_c = tagged_entity_a == tagged_entity_c
        actual_a_not_equals_c = tagged_entity_a != tagged_entity_c

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)

    def test__hash__should_be_hashable__when_has_no_tags(self) -> None:
        # Arrange
        tags = TaggedEntity()

        # Act
        def action(): _ = {tags}

        # Assert
        action()

    def test__hash__should_be_hashable__when_has_tags(self) -> None:
        # Arrange
        tags = TaggedEntity(tags={anon_tag()})

        # Act
        def action(): _ = {tags}

        # Assert
        action()


class _Other(BaseEntity):
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
