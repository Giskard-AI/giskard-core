"""Tests for discriminated union functionality."""

import pytest
from giskard.core import Discriminated, discriminated_base


@discriminated_base
class Animal(Discriminated):
    """Base class for animals."""

    name: str


class Pet(Animal):
    """Base class for pets."""

    name: str


@Animal.register("tigger")
class Tigger(Pet):
    """A tigger."""

    stripes: int = 100


@Animal.register("cat")
class Cat(Pet):
    """A cat."""

    lives: int = 9


# Registering as Pet should work as well (same behavior as registering as Animal)
@Pet.register("dog")
class Dog(Pet):
    """A dog."""

    breed: str


@pytest.mark.parametrize(
    "animal,kind",
    [
        (Tigger(name="Tigger", stripes=100), "tigger"),
        (Dog(name="Buddy", breed="Labrador"), "dog"),
        (Cat(name="Whiskers", lives=9), "cat"),
    ],
)
def test_discriminated_base_registration(animal: Animal, kind: str):
    """Test that discriminated_base decorator registers the base class."""
    assert animal.kind == kind

    model_dump = animal.model_dump()
    assert model_dump["kind"] == kind
    assert model_dump["name"] == animal.name

    assert Animal.model_validate(model_dump) == animal


@pytest.mark.parametrize(
    "animal,kind",
    [
        (Dog(name="Buddy", breed="Labrador"), "dog"),
        (Cat(name="Whiskers", lives=9), "cat"),
    ],
)
def test_discriminated_base_model_validate_subclass(animal: Animal, kind: str):
    """Test that discriminated_base decorator registers the base class."""
    assert animal.kind == kind

    model_dump = animal.model_dump()
    assert model_dump["kind"] == kind
    assert model_dump["name"] == animal.name

    assert Pet.model_validate(model_dump) == animal


def test_discriminated_invalid_kind():
    """Test that invalid kind raises an error."""
    data = {"kind": "elephant", "name": "Dumbo", "age": 10}
    with pytest.raises(ValueError, match="Kind elephant is not registered"):
        Animal.model_validate(data)


def test_discriminated_missing_kind():
    """Test that missing kind raises an error."""
    data = {"name": "Felix", "lives": 9}
    with pytest.raises(ValueError, match="Kind is not provided"):
        Animal.model_validate(data)


@discriminated_base
class GenericAnimal[T](Discriminated):
    """Base class for generic animals."""

    name: str
    value: T


class GenericPet[T](GenericAnimal[T]):
    """Base class for generic pets."""


@GenericAnimal.register("dog")
class GenericDog[T](GenericPet[T]):
    """A dog."""

    breed: str


@GenericPet.register("cat")
class GenericCat[T](GenericPet[T]):
    """A cat."""

    lives: int


@GenericAnimal.register("tigger")
class GenericTigger[T](GenericPet[T]):
    """A tigger."""

    stripes: int


@pytest.mark.parametrize(
    "animal,kind",
    [
        (GenericDog[int](name="Buddy", value=100, breed="Labrador"), "dog"),
        (GenericCat[str](name="Whiskers", value="Meow", lives=9), "cat"),
        (GenericTigger[float](name="Tigger", value=1.0, stripes=100), "tigger"),
    ],
)
def test_discriminated_generic_base_registration[T](
    animal: GenericAnimal[T], kind: str
):
    """Test that discriminated_base decorator registers the base class."""
    assert animal.kind == kind

    model_dump = animal.model_dump()
    assert model_dump["kind"] == kind
    assert model_dump["name"] == animal.name
    assert model_dump["value"] == animal.value
