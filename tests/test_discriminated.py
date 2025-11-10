"""Tests for discriminated union functionality."""

import pytest
from giskard.core import Discriminated, discriminated_base


@discriminated_base
class Animal(Discriminated):
    """Base class for animals."""

    name: str


@Animal.register("dog")
class Dog(Animal):
    """A dog."""

    breed: str


@Animal.register("cat")
class Cat(Animal):
    """A cat."""

    lives: int = 9


def test_discriminated_base_registration():
    """Test that discriminated_base decorator registers the base class."""
    dog = Dog(name="Buddy", breed="Labrador")
    assert dog.kind == "dog"
    assert dog.name == "Buddy"
    assert dog.breed == "Labrador"


def test_discriminated_serialization():
    """Test that discriminated types can be serialized and deserialized."""
    dog = Dog(name="Buddy", breed="Labrador")
    serialized = dog.model_dump()
    assert serialized["kind"] == "dog"
    assert serialized["name"] == "Buddy"
    assert serialized["breed"] == "Labrador"


def test_discriminated_deserialization():
    """Test that discriminated types can be deserialized from dict."""
    data = {"kind": "dog", "name": "Buddy", "breed": "Labrador"}
    animal = Animal.model_validate(data)
    assert isinstance(animal, Dog)
    assert animal.name == "Buddy"
    assert animal.breed == "Labrador"


def test_discriminated_multiple_types():
    """Test that multiple discriminated types can coexist."""
    dog = Dog(name="Buddy", breed="Labrador")
    cat = Cat(name="Whiskers", lives=9)

    dog_data = dog.model_dump()
    cat_data = cat.model_dump()

    assert Animal.model_validate(dog_data).kind == "dog"
    assert Animal.model_validate(cat_data).kind == "cat"


def test_discriminated_invalid_kind():
    """Test that invalid kind raises an error."""
    data = {"kind": "invalid", "name": "Unknown"}
    with pytest.raises(ValueError, match="Kind invalid is not registered"):
        Animal.model_validate(data)


def test_discriminated_missing_kind():
    """Test that missing kind raises an error."""
    data = {"name": "Unknown"}
    with pytest.raises(ValueError, match="Kind is not provided"):
        Animal.model_validate(data)


def test_discriminated_direct_instantiation():
    """Test that subclasses can be instantiated directly."""
    dog = Dog(name="Buddy", breed="Labrador")
    assert dog.kind == "dog"
    assert isinstance(dog, Animal)
    assert isinstance(dog, Dog)
