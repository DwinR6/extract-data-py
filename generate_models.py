import os
import re

# Ruta del archivo SQL con los CREATE TABLE
SQL_FILE = "dump_mysql.sql"

# Carpeta donde se generarán los modelos
MODELS_FOLDER = "modelos"

# Crear carpeta si no existe
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Leer archivo SQL
with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql = f.read()

# Buscar bloques CREATE TABLE
tables = re.findall(r"CREATE TABLE `(\w+)` \((.*?)\);", sql, re.DOTALL)

def to_class_name(table_name):
    return ''.join(word.capitalize() for word in table_name.split('_'))

for table_name, table_body in tables:
    class_name = to_class_name(table_name)
    model_path = os.path.join(MODELS_FOLDER, f"{class_name}.php")

    # Detectar columnas para $fillable
    columns = re.findall(r"`(\w+)`", table_body)
    fillable = ',\n        '.join(f"'{col}'" for col in columns)

    model_code = f"""<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class {class_name} extends Model
{{
    protected $table = '{table_name}';

    protected $fillable = [
        {fillable}
    ];
}}
"""

    with open(model_path, "w", encoding="utf-8") as f:
        f.write(model_code)

    print(f"✅ Modelo generado: {model_path}")

print("\n🎉 ¡Modelos creados exitosamente en la carpeta 'modelos/'!")
