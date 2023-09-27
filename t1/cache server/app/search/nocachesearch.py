import json
import random
import time
from find_car_by_id import find_car_by_id


if __name__ == '__main__':
    while True:
        print("\nChoose an operation:")
        print("1. Simular Busquedas")
        print("2. Salir")

        choice = input("Enter your choice: ")

        if choice == "1":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            start_time = time.time()  # Inicio del temporizador
            with open('data.json', 'r') as json_file:
                data = json.load(json_file)
                numbers = data['numbers']
                random_index = random.randint(0, len(numbers) - 1)
                random_number = numbers[random_index]

            value = find_car_by_id(int(random_index))
            value = str(value)
            if value:
                print("Key found in JSON. Adding to cache...")
                print(value)
                        
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
print(f"Tiempo de ejecucion: {elapsed_time:.5f} seconds")