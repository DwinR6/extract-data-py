import os
import re
from collections import defaultdict

SQL_FILE = "dump_mysql.sql"  # Aquí pon el nombre de tu archivo SQL
MODELS_FOLDER = "modelos"
os.makedirs(MODELS_FOLDER, exist_ok=True)

with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql = f.read()

# Encontrar bloques CREATE TABLE
create_table_blocks = re.findall(r"CREATE TABLE `(\w+)` \((.*?)\);", sql, re.DOTALL)

tables = {}
foreign_keys = defaultdict(list)

# Parsear cada tabla
for table_name, table_body in create_table_blocks:
    columns = re.findall(r"`(\w+)`", table_body)
    tables[table_name] = {
        'columns': columns,
        'foreign_keys': []
    }

# Detectar relaciones por convención (campo `*_id`)
for table_name, data in tables.items():
    for column in data['columns']:
        if column.endswith("_id"):
            ref_table = column[:-3]  # Eliminar '_id' para obtener el nombre de la tabla
            if ref_table in tables:
                tables[table_name]['foreign_keys'].append({
                    'column': column,
                    'ref_table': ref_table
                })
                foreign_keys[ref_table].append((table_name, column))

# Generar modelos
def to_class_name(name):
    return ''.join(word.capitalize() for word in name.split('_'))

for table_name, data in tables.items():
    class_name = to_class_name(table_name)
    model_path = os.path.join(MODELS_FOLDER, f"{class_name}.php")

    fillable = ',\n        '.join(f"'{col}'" for col in data['columns'])

    # Relaciones belongsTo (por convención _id)
    belongs_to = ""
    for fk in data['foreign_keys']:
        ref_table = fk['ref_table']
        column = fk['column']
        if column == f"{ref_table}_id":
            belongs_to += f"""
    public function {ref_table}()
    {{
        return \$this->belongsTo({to_class_name(ref_table)}::class);
    }}
"""
        else:
            belongs_to += f"""
    public function {ref_table}()
    {{
        return \$this->belongsTo({to_class_name(ref_table)}::class, '{column}');
    }}
"""

    # Relaciones hasMany (por convención _id)
    has_many = ""
    if table_name in foreign_keys:
        for child_table, fk_column in foreign_keys[table_name]:
            has_many += f"""
    public function {child_table}()
    {{
        return \$this->hasMany({to_class_name(child_table)}::class, '{fk_column}');
    }}
"""

    model_code = f"""<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class {class_name} extends Model
{{
    protected $table = '{table_name}';

    protected $fillable = [
        {fillable}
    ];{belongs_to}{has_many}
}}
"""

    with open(model_path, "w", encoding="utf-8") as f:
        f.write(model_code)

    print(f"✅ Modelo generado: {model_path}")

print("\n🎉 ¡Todos los modelos han sido generados con relaciones inferidas!")
