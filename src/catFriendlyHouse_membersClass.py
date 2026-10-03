from src.thingClass import Thing

class Food(Thing):
    def __init__(self, weight=0, calories=0):
        self.weight = weight        # grams
        self.calories = calories    # kcal per 100 g
        self.energy = weight * calories / 100   # total kcal in this item

    def sayHi(self):
        print(f"There is a {type(self).__name__.lower()}")


class Milk(Food):
    def __init__(self, weight=0, calories=0):
        super().__init__(weight, calories)


class Sausage(Food):
    def __init__(self, weight=0, calories=0):
        super().__init__(weight, calories)


class Mouse(Food):
    def __init__(self, size=1):
        super().__init__()
        self.size = size
        self.energy = size * 1000

    def sayHi(self):
        print(f"There is a Mouse with a power {self.energy}")


# Task-3: the Cat can meet a Dog in catFriendlyHouse2_env
class Dog(Thing):
    def sayHi(self):
        print("Woof! There is a Dog")
