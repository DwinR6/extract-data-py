import os
import re
from dbfread import DBF
from collections import defaultdict

# Función para detectar tipo de dato
def detect_type(values):
    is_int = True
    is_float = True
    is_date = True

    for v in values:
        if v is None:
            continue
        if isinstance(v, str):
            v = v.strip()
            if not v:
                continue
        if isinstance(v, float):
            continue
        if isinstance(v, int):
            continue

        try:
            int(v)
        except:
            is_int = False
        try:
            float(v)
        except:
            is_float = False
        if not re.match(r"\d{4}-\d{2}-\d{2}", str(v)):
            is_date = False

    if is_int:
        return "INT"
    elif is_float:
        return "DOUBLE"
    elif is_date:
        return "DATE"
    else:
        return "TEXT"

# Carpeta con los archivos DBF + CDX + FPT
DBF_FOLDER = r"C:\Users\E_noe\Repos\Aspescu data"
OUTPUT_SQL = "dump_mysql.sql"
MODELS_FOLDER = "aspescu/models"
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Diccionario para almacenar las tablas
tables = {}

# Generar el dump SQL de las tablas
with open(OUTPUT_SQL, "w", encoding="utf-8") as out_sql:
    for file_name in os.listdir(DBF_FOLDER):
        if not file_name.lower().endswith(".dbf"):
            continue

        table_name = os.path.splitext(file_name)[0]
        dbf_path = os.path.join(DBF_FOLDER, file_name)
        print(f"Procesando {file_name}...")

        # Carga de datos (dbfread usa .fpt automáticamente si existe)
        table = DBF(dbf_path, load=True, ignore_missing_memofile=False)
        columns = table.field_names

        # Detectar tipos de datos
        column_data = {col: [] for col in columns}
        for record in table:
            for col in columns:
                column_data[col].append(record[col])

        column_definitions = []
        for col in columns:
            col_name = col.replace(" ", "_")
            col_type = detect_type(column_data[col])
            column_definitions.append(f"`{col_name}` {col_type}")

        create_stmt = f"DROP TABLE IF EXISTS `{table_name}`;\n"
        create_stmt += f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(column_definitions) + "\n);\n\n"
        out_sql.write(create_stmt)

        # Insertar registros
        for record in table:
            values = []
            for col in columns:
                val = record[col]
                if val is None:
                    values.append("NULL")
                elif isinstance(val, str):
                    val = val.replace("'", "''")
                    values.append(f"'{val}'")
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    values.append(f"'{str(val)}'")
            insert_stmt = f"INSERT INTO `{table_name}` VALUES ({', '.join(values)});\n"
            out_sql.write(insert_stmt)

        # Generar índices sugeridos basados en nombres de columnas
        for col in columns:
            index_stmt = f"CREATE INDEX `idx_{col}` ON `{table_name}` (`{col}`);\n"
            out_sql.write(index_stmt)

        out_sql.write("\n-- ----------------------------------------\n\n")

        # Almacenar las tablas
        tables[table_name] = columns

    print(f"✅ Dump completado. Archivo generado: {OUTPUT_SQL}")

# Función para detectar relaciones
def detect_relationships(tables):
    relationships = defaultdict(list)

    for table_name, columns in tables.items():
        for col in columns[1:]:  # Empezamos desde la segunda columna (la primera es la PK)
            # Buscar una relación con alguna tabla
            related_table_name = None
            for other_table_name in tables.keys():
                if other_table_name != table_name and col.lower() in other_table_name.lower():
                    related_table_name = other_table_name
                    break
            
            if related_table_name:
                relationships[table_name].append({
                    'field': col,
                    'related_table': related_table_name
                })
    
    return relationships

# Identificar relaciones
relationships = detect_relationships(tables)

# Generar los modelos Laravel con relaciones
for table_name, columns in tables.items():
    model_code = f"""<?php

namespace App\Aspescu\Models;

use Illuminate\Database\Eloquent\Model;

class {table_name.capitalize()} extends Model
{{
    protected $table = '{table_name}';

    protected $fillable = [
        {', '.join([f"'{col}'" for col in columns])}
    ];
"""

    # Añadir relaciones detectadas
    if table_name in relationships:
        for rel in relationships[table_name]:
            field_name = rel['field']
            related_table_name = rel['related_table']
            model_code += f"""
    public function {related_table_name}()
    {{
        return $this->belongsTo({related_table_name.capitalize()}::class, '{field_name}');
    }}
"""

    model_code += "}\n"

    # Guardar modelo
    with open(os.path.join(MODELS_FOLDER, f"{table_name.capitalize()}.php"), "w", encoding="utf-8") as model_file:
        model_file.write(model_code)
        print(f"Modelo generado para la tabla: {table_name}")

print(f"\n🎉 ¡Modelos generados en la carpeta '{MODELS_FOLDER}' con relaciones inferidas!")
