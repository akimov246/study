def handle_command(message):
    match message:
        case ["BEEPER", frequency, times]:
            print(frequency, times)
        case ["NECK", angle]:
            print(angle)
        case ["LED", ident, intensity]:
            print(ident, intensity)
        case ["LED", ident, red, green, blue]:
            print(ident, red, green, blue)
        case _:
            raise InvalidCommand(message)

class InvalidCommand(Exception):
    def __init__(self, message):
        self.message = f"Неверная команда: {message}"

    def __str__(self):
        return self.message

def what_country_number(number: str):
    try:
        print(number.split("-"))
        match number.split("-"):
            case ["+7" | "8", *rest]:
                return "Russia"
            case ["+380", *rest]:
                return "Ukraine"
            case _:
                raise Exception("Error")
    except Exception as e:
        return e

if __name__ == "__main__":
    number1 = "+7-983-292-33-84"
    number2 = "+380-937-181-083"
    number3 = "+1488-228-1337"
    print(what_country_number(number1))
    print(what_country_number(number2))
    print(what_country_number(number3))