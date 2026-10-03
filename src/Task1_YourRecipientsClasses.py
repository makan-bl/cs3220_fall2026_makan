from src.thingClass import Thing

class OfficeManager(Thing):
  def __init__(self, name='Joe'):
    self.name = name
    print(f"I am OfficeManager {self.name}")

class ITStaff(Thing):
  def __init__(self, name='Jack'):
    self.name = name
    print(f"I am ITStaff {self.name}")

class Student(Thing):
  def __init__(self, name='Hanna'):
    self.name = name
    print(f"I am Student {self.name}")
