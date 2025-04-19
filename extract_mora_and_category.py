import pandas as pd

# Ruta del archivo Excel
excel_file = "inforedmarzo25.xlsx"

# Leer las columnas indicadas (por índice)
df = pd.read_excel(excel_file, usecols=[0, 1, 4, 9, 10, 13, 14, 15, 19, 26, 29], header=None)

# Nombrar las columnas para mejor referencia
df.columns = [
    "ano", "mes", "Num_Pto", "saldo", "mora", 
    "linea_cre", "dias_mora", "utl_pag", "dia_reporte", 
    "calif_actual", "est_credito"  # est_credito será el ID del préstamo (loan)
]

# Convertir Num_Pto a entero (puedes manejar errores si es necesario)
df["Num_Pto"] = pd.to_numeric(df["Num_Pto"], errors='coerce').fillna(0).astype(int)

# Archivo donde se guardarán las consultas
output_file = "consultas_generadas.sql"

with open(output_file, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        loan_id = row["Num_Pto"]  # ID del préstamo (loan) como entero
        linea_cred = row["linea_cre"]

        # Consulta UPDATE
        f.write(f"UPDATE loan_application SET infored_category = '{linea_cred}' WHERE loan_id = {loan_id};\n")

        # Consulta INSERT
        f.write(
            "INSERT INTO infored_statements (year, month, loan_id, balance, penalty_amount, classification, penalty_days, last_payment_date, day, status) "
            f"VALUES ({row['ano']}, {row['mes']}, {loan_id}, {row['saldo']}, {row['mora']}, '{row['calif_actual']}', "
            f"{row['dias_mora']}, '{row['utl_pag']}', {row['dia_reporte']}, '{row['est_credito']}');\n\n"
        )

print(f"✅ Consultas generadas correctamente en '{output_file}'")
