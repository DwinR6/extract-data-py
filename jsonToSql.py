import json
import os

# Ruta del archivo JSON y archivo SQL
json_filename = 'datos_clientes.json'
sql_filename = 'insert_data.sql'

# Función para manejar claves faltantes
def get_value(data, key, default=None):
    return data.get(key, default)

# Función principal que genera las sentencias SQL
def generate_sql_insert(json_data):
    sql_statements = []

    for  datos in json_data:
        # capitalize the first letter of the first name
        nombre_completo = datos.get('cliente', '').split()
        first_name = nombre_completo[0] if len(nombre_completo) > 0 else ''
        second_name = nombre_completo[1] if len(nombre_completo) > 1 else ''
        first_surname = nombre_completo[2] if len(nombre_completo) > 2 else ''
        second_surname = nombre_completo[3] if len(nombre_completo) > 3 else ''
        
        #si el nombre completo tiene 'de' configurar como married_name
        if 'de' in nombre_completo:
            married_name = nombre_completo[nombre_completo.index('de') + 1] if len(nombre_completo) > 2 else ''
        else:
            married_name = ''

        #capitalize the first letter of names
        first_name = first_name.capitalize()
        second_name = second_name.capitalize()
        first_surname = first_surname.capitalize()
        second_surname = second_surname.capitalize()
        married_name = married_name.capitalize()

        # Insert for clients table
        insert_clients = f"""
        INSERT INTO clients (client_id, employee_id, registration_date, client_type_id, first_name, second_name, first_surname, second_surname, married_name, family_status_id, phone_number, cellphone_number, identification_type_id, identification_number, nit_homologation) 
        VALUES ('{get_value(datos, 'n_credito', 'NULL')}', '{get_value(datos, 'asesor', '1')}', NOW(), 1, '{first_name}', '{second_name}', '{first_surname}', '{second_surname}', '{married_name}', 1, 's/a', 0, 1, '{get_value(datos, 'dui', '')}', 'true');"""
        sql_statements.append(insert_clients)

        # Insert for loan_applications table
        insert_loan_applications = f"""
        INSERT INTO loan_applications (loan_application_id, loan_application_number, application_date, agency_id, client_id, employee_id, destination_id, guarantee_type_id, amount, term, status) VALUES ({get_value(datos, 'n_credito', 'NULL')}, LPAD({get_value(datos, 'n_credito', 'NULL')}, 8, '0'), '{get_value(datos, 'fecha_aprobacion', 'NULL')}', 1, {get_value(datos, 'n_credito', 'NULL')}, {get_value(datos, 'asesor', '1')}, 1, 1, {get_value(datos, 'monto_aprobado', get_value(datos, 'monto', '0'))}, {get_value(datos, 'plazo', '12')}, 'approved');"""
        sql_statements.append(insert_loan_applications)

        # Insert for loans table
        insert_loans = f"""
        INSERT INTO loans (loan_id, loan_number, loan_application_id, destination_id, approval_date, outlay_date, due_date, last_payment_date, next_payment_date, balance, status) VALUES ({get_value(datos, 'n_credito', 'NULL')}, LPAD({get_value(datos, 'n_credito', 'NULL')}, 9, '0'), {get_value(datos, 'n_credito', 'NULL')}, 1, '{get_value(datos, 'fecha_aprobacion', 'NULL')}', {get_value(datos, 'fecha_desembolso', 'NULL')}, NULL, '{get_value(datos, 'ultima_fecha_pago', 'NULL')}', NULL, {get_value(datos, 'saldo', 'NULL')}, 'in_progress');"""
        sql_statements.append(insert_loans)

        # Insert for loan_deductions table
        insert_loan_deductions = f"""
        INSERT INTO loan_deductions (loan_deduction_id, loan_id, financial_advice, iva_financial_advice, notarial_charges, registration_expenses, balance_cancellation, loan_cancellation_id, other_expenses, total_deductions, other_expenses_description) VALUES ({get_value(datos, 'n_credito', 'NULL')}, {get_value(datos, 'n_credito', 'NULL')}, {get_value(datos, 'asesoria_financiera', 'NULL')}, {get_value(datos, 'iva', 'NULL')}, 0, 0, 0, NULL, {get_value(datos, 'otros', 'NULL')}, {get_value(datos, 'total_descuentos', 'NULL')}, '' );"""
        sql_statements.append(insert_loan_deductions)

        # Insert for outlay_conditions table
        insert_outlay_conditions = f"""
        INSERT INTO outlay_conditions (outlay_condition_id, loan_id, type, date, place, amount, cash_to, check_to, bank, bank_account_number, bank_account_owner, local_account_number, local_account_owner) VALUES (NULL, {get_value(datos, 'n_credito', 'NULL')}, 1, '{get_value(datos, 'fecha_desembolso', 'NULL')}', 'Agencia Central', {get_value(datos, 'desembolso_cliente', 'NULL')}, NULL, NULL, NULL, NULL, NULL, NULL, NULL);"""
        sql_statements.append(insert_outlay_conditions)

        # Insert for amortizations table, of App\Models\Loan
        insert_amortizations = f"""
        INSERT INTO amortizations (amortization_id, amortizationable_id, amortizationable_type, date, amount, term, interest_rate, include_iva, include_insurance, payment, payment_frequency_id, amortization_method_id, last_payment_date)  VALUES ( NULL, {get_value(datos,'n_credito','NULL')},  'App\\\\Models\\\\Loan',  '{get_value(datos, 'fecha_aprobacion', 'NULL')}',  {get_value(datos, 'monto_aprobado', get_value(datos, 'monto', '0'))},  {get_value(datos, 'plazo', '12')},  {get_value(datos, 'interes', '0')}, {get_value(datos, 'iva', 'NULL')}, '{get_value(datos, 'seguro', '0')}', {get_value(datos, 'valor_cuota', '0')}, {get_value(datos, 'forma_pago', get_value(datos, 'periodo', '1'))}, 2, '{get_value(datos, 'ultima_fecha_pago', 'NULL')}');"""
        sql_statements.append(insert_amortizations)

        # Insert for amortizations table, of App\Models\LoanApplication
        insert_amortizations_loan_application = f"""
        INSERT INTO amortizations (amortization_id, amortizationable_id, amortizationable_type, date, amount, term, interest_rate, include_iva, include_insurance, payment, payment_frequency_id, amortization_method_id, last_payment_date) VALUES ( NULL, {get_value(datos,'n_credito','NULL')}, 'App\\\\Models\\\\LoanApplication', '{get_value(datos, 'fecha_aprobacion', 'NULL')}', {get_value(datos, 'monto_aprobado', get_value(datos, 'monto', '0'))}, {get_value(datos, 'plazo', '12')}, {get_value(datos, 'interes', '0')}, {get_value(datos, 'iva', 'NULL')}, {get_value(datos, 'seguro', '0')}, {get_value(datos, 'valor_cuota', '0')}, {get_value(datos, 'forma_pago', get_value(datos, 'forma_pago', '1'))}, 2, '{get_value(datos, 'ultima_fecha_pago', 'NULL')}');"""

        
        sql_statements.append(insert_amortizations_loan_application)

        sql_statements.append('\n')

    return sql_statements

def main():
    # Leer el archivo JSON
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Generar las sentencias SQL
    sql_statements = generate_sql_insert(data)

    # Guardar las sentencias SQL en un archivo
    with open(sql_filename, 'w', encoding='utf-8') as f:
        f.write(''.join(sql_statements))

    print(f"SQL insert statements written to {sql_filename}")

if __name__ == '__main__':
    main()
