import json

# Crear datos de prueba
data = {f"key_{i}": f"value_{i}" for i in range(1, 1000001)}

# Escribir los datos en un archivo JSON
with open("data.json", "w") as file:
    json.dump(data, file)

print("Archivo JSON generado con éxito.")
