import re

# Archivo de entrada con los inserts originales
input_file = "billing_inserts.sql"
output_file = "billing_inserts_updated.sql"

# Clase relacionada para la estructura polimórfica
DEFAULT_POLYMORPHIC_TYPE = "App\\Models\\LoanPaymentModel"

# Leer el archivo de entrada
with open(input_file, "r", encoding="utf-8") as infile:
    data = infile.read()

# Verificar si los datos se están leyendo correctamente
if not data:
    print(f"El archivo {input_file} está vacío o no se pudo leer.")
else:
    print(f"Se leyeron {len(data)} caracteres del archivo de entrada.")

# Expresión regular para encontrar los INSERTS
insert_pattern = re.compile(
    r"INSERT INTO `cashbox_transaction` \(.*?\) VALUES \((.*?)\);",
    re.DOTALL
)

# Procesar los matches y transformar los datos
updated_inserts = []

# Verificar si encontramos coincidencias
matches_found = False

for match in insert_pattern.finditer(data):
    matches_found = True
    values = match.group(1)  # Captura los valores dentro de VALUES (...)

    # Dividir los valores originales por coma, respetando las comillas
    fields = re.split(r",(?=(?:[^\']*\'[^\']*\')*[^\']*$)", values)

    # Mapear los campos a la nueva estructura
    id_transaction = fields[0].strip()
    payment_id = fields[3].strip()
    
    # Asignar valores a las nuevas columnas
    cashbox_transactionable_id = loan_payment_id
    cashbox_transactionable_type = f"'{DEFAULT_POLYMORPHIC_TYPE}'"

    # Mantener los demás campos, asegurándose de agregar comillas para los valores de tipo cadena
    id_document_type = fields[1].strip()
    document_fiscal_number = fields[2].strip()
    amount = fields[4].strip()
    date = fields[5].strip()
    status = fields[6].strip()
    created_at = fields[7].strip()
    updated_at = fields[8].strip()

    # Formatear los valores para las columnas con comillas (si es necesario)
    def format_value(value):
        # Si el valor es numérico (sin comillas), devolverlo tal cual
        if value.isdigit():
            return value
        # Si el valor tiene comillas, ya está bien formateado
        elif value.startswith("'") and value.endswith("'"):
            return value
        # Si el valor es una cadena, agregar comillas
        return f"'{value}'"

    # Crear el nuevo INSERT con los valores formateados
    new_insert = (
        f"INSERT INTO `billing` (id_billing, cashbox_transactionable_id, cashbox_transactionable_type, id_document_type, "
        f"document_fiscal_number, amount, date, status, created_at, updated_at) VALUES ("
        f"{format_value(id_billing)}, {format_value(cashbox_transactionable_id)}, {cashbox_transactionable_type}, "
        f"{format_value(id_document_type)}, {format_value(document_fiscal_number)}, {format_value(amount)}, "
        f"{format_value(date)}, {format_value(status)}, {format_value(created_at)}, {format_value(updated_at)});"
    )

    updated_inserts.append(new_insert)

# Verificar si encontramos alguna coincidencia
if not matches_found:
    print("No se encontraron coincidencias con el patrón de INSERT INTO.")
else:
    print(f"Se encontraron {len(updated_inserts)} registros para procesar.")

# Escribir el archivo actualizado solo si hay registros procesados
if updated_inserts:
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(updated_inserts))
    print(f"Se generó el archivo actualizado: {output_file}")
else:
    print("No se generó ningún archivo, ya que no se encontraron registros.")
