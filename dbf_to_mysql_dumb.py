import os
from dbfread import DBF
import re

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

# Carpeta que contiene los archivos DBF
DBF_FOLDER = r"C:\Users\E_noe\Repos\Aspescu data"

OUTPUT_SQL = "dump_mysql.sql"

with open(OUTPUT_SQL, "w", encoding="utf-8") as out_sql:
    for file_name in os.listdir(DBF_FOLDER):
        if not file_name.lower().endswith(".dbf"):
            continue

        table_name = os.path.splitext(file_name)[0]
        dbf_path = os.path.join(DBF_FOLDER, file_name)
        print(f"Procesando {file_name}...")

        table = DBF(dbf_path, load=True)
        columns = table.field_names

        # Detectar tipos de datos por columna
        column_data = {col: [] for col in columns}
        for record in table:
            for col in columns:
                column_data[col].append(record[col])

        column_definitions = []
        for col in columns:
            col_name = col.replace(" ", "_")
            col_type = detect_type(column_data[col])
            column_definitions.append(f"`{col_name}` {col_type}")

        create_stmt = f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(column_definitions) + "\n);\n\n"
        out_sql.write(create_stmt)

        # Insertar datos
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

        out_sql.write("\n-- ----------------------------------------\n\n")

print(f"✅ Dump completado. Archivo generado: {OUTPUT_SQL}")

