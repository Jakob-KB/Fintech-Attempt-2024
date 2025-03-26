class Car:
    def __init__(self, color, mileage):
        self.color = color
        self.mileage = mileage

    def print_car_colour(self):
        print(self.color)


my_car = Car(
    color="red",
    mileage=20
)
