"""Exemplo de como definir uma interface ou tipo de dado em Python."""

from pydantic import BaseModel


# Definindo uma interface em Python
class IExample:
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age

    def __str__(self) -> str:
        return f"Name: {self.name}, Age: {self.age}"


def create_person(person: IExample):
    return person.age, person.name


new_person = create_person(IExample("Bruno", 25))

print(new_person)  # Output: (25, 'Bruno')


person_2: IExample = IExample("Maria", 30)

person_2.age = 31

print(person_2)

# No entanto é possível e até melhor usar o pydantic para definir interfaces em Python


class Person(BaseModel):
    name: str
    age: int


person_3 = Person(name="Maria", age=30)

print(person_3.age)
print(person_3)
