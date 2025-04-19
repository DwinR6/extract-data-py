import re

INPUT_SQL = "dump_mysql.sql"
OUTPUT_SQL = "estructura_solo_tablas.sql"

def limpiar_linea(linea):
    return linea.strip().rstrip(',')

def extraer_estructura_sin_restricciones(contenido):
    tablas = {}
    bloques_tabla = re.findall(r"CREATE TABLE\s+`(\w+)`\s*\((.*?)\)[^;]*;", contenido, re.DOTALL | re.IGNORECASE)

    for nombre_tabla, bloque in bloques_tabla:
        lineas = bloque.strip().split("\n")
        columnas = []
        for linea in lineas:
            linea = limpiar_linea(linea)
            if linea.startswith("`"):
                # Es una columna
                campo = re.match(r"`(\w+)`\s+([^,]+)", linea)
                if campo:
                    nombre_campo = campo.group(1)
                    tipo_campo = campo.group(2).split()[0]  # Solo el tipo (ej. INT, VARCHAR)
                    columnas.append((nombre_campo, tipo_campo))
        tablas[nombre_tabla] = columnas

    return tablas

def generar_sql_estructura(tablas):
    resultado = ""
    for nombre_tabla, columnas in tablas.items():
        resultado += f"CREATE TABLE `{nombre_tabla}` (\n"
        resultado += ",\n".join([f"  `{col}` {tipo}" for col, tipo in columnas])
        resultado += "\n);\n\n"
    return resultado

def main():
    with open(INPUT_SQL, "r", encoding="utf-8") as f:
        contenido = f.read()

    tablas = extraer_estructura_sin_restricciones(contenido)
    sql_generado = generar_sql_estructura(tablas)

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write(sql_generado)

    print(f"✅ Estructura de tablas extraída en '{OUTPUT_SQL}' sin PK ni FK.")

if __name__ == "__main__":
    main()
