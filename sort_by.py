import json

def ordenar_json(json_file, output_file, key="cliente"):
    try:
        # Cargar el JSON desde el archivo
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validar si es una lista de objetos
        if not isinstance(data, list):
            raise ValueError("El JSON no tiene la estructura esperada: debe ser una lista de objetos.")

        # Ordenar los datos según la clave especificada
        data_sorted = sorted(data, key=lambda x: x.get(key, "").lower())

        # Guardar el JSON ordenado en un nuevo archivo
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data_sorted, file, ensure_ascii=False, indent=4)

        print(f"JSON ordenado guardado en: {output_file}")
    except Exception as e:
        print(f"Error al procesar el JSON: {e}")

# Especificar los archivos y la clave para ordenar
json_input_path = "datos_clientes.json"  # Reemplaza con la ruta de tu archivo JSON de entrada
json_output_path = "clientes_ordenados.json"  # Archivo de salida con el JSON ordenado
ordenar_clave = "n_credito"  # Clave para ordenar

# Ordenar el JSON
ordenar_json(json_input_path, json_output_path, key=ordenar_clave)
