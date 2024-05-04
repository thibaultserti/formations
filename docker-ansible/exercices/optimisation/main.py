import sys
from datetime import datetime

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <DD-MM-YYYY>")
        return

    date_str = sys.argv[1]

    try:
        # Conversion de la chaîne de caractères en objet datetime
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        # Obtention du jour de la semaine
        day_of_week = date_obj.strftime('%A')
        print(f"The day of the week for {date_str} is {day_of_week}.")
    except ValueError:
        print("Invalid date format. Please use DD-MM-YYYY.")

if __name__ == "__main__":
    main()
