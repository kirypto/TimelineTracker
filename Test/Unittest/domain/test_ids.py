from random import choices, choice
from string import ascii_letters
from unittest import TestCase
from uuid import uuid4, uuid3, uuid1, NAMESPACE_URL, uuid5

from domain.ids import PrefixedUUID, IdentifiedEntity


def anon_id_prefix(num_digits: int = 10) -> str:
    return "".join(choices(ascii_letters + "_", k=num_digits))


def anon_prefixed_id() -> PrefixedUUID:
    return PrefixedUUID(anon_id_prefix(20), uuid4())


class TestPrefixedUUID(TestCase):
    def test__init__should_reject_non_alpha_numeric_prefix(self) -> None:
        # Arrange
        illegal_prefix = anon_id_prefix(4) + choice("!@#$%^&*()+={}[]|\\:;"'<>,.?/-')
        id = uuid4()

        # Act
        def Action(): PrefixedUUID(illegal_prefix, id)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__init__should_reject_non_version_4_uuids(self) -> None:
        # Arrange
        uuid_of_wrong_version = choice([uuid1(), uuid3(NAMESPACE_URL, "nope"), uuid5(NAMESPACE_URL, "nope")])

        # Act
        def Action(): PrefixedUUID(anon_id_prefix(), uuid_of_wrong_version)

        # Assert
        self.assertRaises(ValueError, Action)

    def test__str__should_return_prefixed_id_as_str(self) -> None:
        # Arrange
        prefix = anon_id_prefix()
        uuid = uuid4()
        id = PrefixedUUID(prefix, uuid)
        expected = f"{prefix}-{uuid}"

        # Act
        actual = str(id)

        # Assert
        self.assertEqual(expected, actual)

    def test__equality__should_compare_prefixed_ids(self) -> None:
        # Arrange
        prefix_1 = anon_id_prefix()
        prefix_2 = anon_id_prefix()
        uuid_1 = uuid4()
        uuid_2 = uuid4()
        id_a = PrefixedUUID(prefix_1, uuid_1)
        id_b = PrefixedUUID(prefix_1, uuid_1)
        id_c = PrefixedUUID(prefix_2, uuid_1)
        id_d = PrefixedUUID(prefix_1, uuid_2)

        # Act
        actual_a_equals_b = id_a == id_b
        actual_a_not_equals_b = id_a != id_b
        actual_a_equals_c = id_a == id_c
        actual_a_not_equals_c = id_a != id_c
        actual_a_equals_d = id_a == id_d
        actual_a_not_equals_d = id_a != id_d

        # Assert
        self.assertTrue(actual_a_equals_b)
        self.assertFalse(actual_a_not_equals_b)
        self.assertFalse(actual_a_equals_c)
        self.assertTrue(actual_a_not_equals_c)
        self.assertFalse(actual_a_equals_d)
        self.assertTrue(actual_a_not_equals_d)

    def test__hash__should_be_hashable(self) -> None:
        # Arrange
        id = anon_prefixed_id()

        # Act
        def Action(): _ = {id}

        # Assert
        Action()


class TestIdentifiedEntity(TestCase):
    def test__init__should_accept_id(self) -> None:
        # Arrange

        # Act
        def Action(): _ = IdentifiedEntity(id=anon_prefixed_id())

        # Assert
        Action()

    def test__init__should_accept_kwargs(self) -> None:
        # Arrange
        class TestKwargs(IdentifiedEntity, _Other):
            pass

        # Act
        expected = "other"

        def Action(): return TestKwargs(id=anon_prefixed_id(), other=expected)
        actual = Action()

        # Assert
        self.assertEqual(expected, actual.other)

    def test__id__should_return_prefixed_id(self) -> None:
        # Arrange
        expected = anon_prefixed_id()
        entity = IdentifiedEntity(id=expected)

        # Act
        actual = entity.id

        # Assert
        self.assertEqual(expected, actual)

    def test__id__should_not_be_settable(self) -> None:
        # Arrange
        entity = IdentifiedEntity(id=anon_prefixed_id())

        # Act
        def Action(): entity.id = anon_prefixed_id()

        # Assert
        self.assertRaises(AttributeError, Action)


class _Other:
    def __init__(self, other, **kwargs):
        self.other = other
        super().__init__(**kwargs)
