import os
import re

MODELS_DIR = "Aspescu/Models"
CONTROLLERS_DIR = "app/Http/Controllers/Aspescu"
SERVICES_DIR = "app/Services/Aspescu"
VIEWS_DIR = "resources/views/aspescu"
ROUTES_FILE = "routes/web.php"

os.makedirs(CONTROLLERS_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(VIEWS_DIR, exist_ok=True)
#crear archivo de rutas si no existe
if not os.path.exists(ROUTES_FILE):
    with open(ROUTES_FILE, "w", encoding="utf-8") as f:
        f.write("<?php\n\nuse Illuminate\Support\Facades\Route;\n\n")



def snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def parse_models():
    tables = {}

    for file in os.listdir(MODELS_DIR):
        if file.endswith(".php"):
            with open(os.path.join(MODELS_DIR, file), "r", encoding="utf-8") as f:
                content = f.read()
                class_match = re.search(r"class\s+(\w+)", content)
                if not class_match:
                    continue
                model_name = class_match.group(1)
                table_name = snake_case(model_name)

                fillable_match = re.search(r"protected\s+\$fillable\s+=\s+\[(.*?)\];", content, re.DOTALL)
                if fillable_match:
                    fields_raw = fillable_match.group(1)
                    fields = re.findall(r"'(.*?)'", fields_raw)
                else:
                    fields = []

                if "id" not in fields:
                    fields = ["id"] + fields

                tables[model_name] = {
                    "table": table_name,
                    "fields": fields
                }

    return tables

def generate_controller(model_name, table, fields):
    controller_path = os.path.join(CONTROLLERS_DIR, f"{model_name}Controller.php")
    with open(controller_path, "w", encoding="utf-8") as f:
        f.write(f"""<?php

namespace App\Http\Controllers\Aspescu;

use App\Http\Controllers\Controller;
use App\Models\Aspescu\{model_name};
use App\Services\Aspescu\{model_name}Service;
use Illuminate\Http\Request;

class {model_name}Controller extends Controller
{{
    protected $service;

    public function __construct({model_name}Service $service)
    {{
        $this->service = $service;
    }}

    public function index()
    {{
        $items = $this->service->all();
        return view('aspescu.{table}.index', compact('items'));
    }}

    public function create()
    {{
        return view('aspescu.{table}.create');
    }}

    public function store(Request $request)
    {{
        $this->service->create($request->all());
        return redirect()->route('{table}.index');
    }}

    public function edit($id)
    {{
        $item = $this->service->find($id);
        return view('aspescu.{table}.edit', compact('item'));
    }}

    public function update(Request $request, $id)
    {{
        $this->service->update($id, $request->all());
        return redirect()->route('{table}.index');
    }}

    public function destroy($id)
    {{
        $this->service->delete($id);
        return redirect()->route('{table}.index');
    }}
}}
""")

def generate_service(model_name):
    service_path = os.path.join(SERVICES_DIR, f"{model_name}Service.php")
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(f"""<?php

namespace App\Services\Aspescu;

use App\Models\Aspescu\{model_name};

class {model_name}Service
{{
    public function all()
    {{
        return {model_name}::all();
    }}

    public function find($id)
    {{
        return {model_name}::findOrFail($id);
    }}

    public function create(array $data)
    {{
        return {model_name}::create($data);
    }}

    public function update($id, array $data)
    {{
        $item = {model_name}::findOrFail($id);
        $item->update($data);
        return $item;
    }}

    public function delete($id)
    {{
        return {model_name}::destroy($id);
    }}
}}
""")

def generate_views(table, fields):
    view_folder = os.path.join(VIEWS_DIR, table)
    os.makedirs(view_folder, exist_ok=True)

    with open(os.path.join(view_folder, "index.blade.php"), "w", encoding="utf-8") as f:
        f.write(f"""@extends('layouts/sections/navigation/navigation')

@section('content')
<div class="card w-100 border p-2 border-0 shadow">
    <div class="card-body">
        <div class="d-flex justify-content-between mb-4 align-items-center">
            <h4 class="text-primary">Listado de {table.capitalize()}</h4>
            <a href="{{{{ route('{table}.create') }}}}" class="btn btn-primary">Crear nuevo</a>
        </div>
        <div class="table-responsive">
            <table class="table table-bordered table-striped">
                <thead class="table-light">
                    <tr>
                        {''.join(f"<th>{field}</th>" for field in fields)}
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($items as $item)
                    <tr>
                        {''.join(f"<td>{{{{ $item->{field} }}}}</td>" for field in fields)}
                        <td>
                            <a href="{{{{ route('{table}.edit', $item->id) }}}}" class="btn btn-sm btn-warning">Editar</a>
                            <form action="{{{{ route('{table}.destroy', $item->id) }}}}" method="POST" style="display:inline-block;">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-sm btn-danger">Eliminar</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>
</div>
@endsection
""")

    for view in ["create", "edit"]:
        action = f"{table}.{'store' if view == 'create' else 'update'}"
        id_part = ", $item->id" if view == "edit" else ""
        method = '@method("PUT")' if view == "edit" else ""
        title = "Editar" if view == "edit" else "Nueva"

        fields_html = "\n".join([
            f"""
                <div class="mb-3">
                    <label class="form-label" for="{field}">{field.capitalize()}</label>
                    <input type="text" class="form-control" name="{field}" id="{field}" value="{{{{ $item->{field} ?? '' }}}}" />
                </div>
            """ for field in fields if field != "id"
        ])

        form_view = f"""@extends('layouts/sections/navigation/navigation')

@section('content')
<div class="card w-100 border p-2 border-0 shadow">
    <div class="card-body">
        <h4 class="text-primary mb-4">{title} {table.capitalize()}</h4>
        <form action="{{{{ route('{action}'{id_part}) }}}}" method="POST">
            @csrf
            {method}
            {fields_html}
            <button type="submit" class="btn btn-primary">Guardar</button>
        </form>
    </div>
</div>
@endsection
"""

        with open(os.path.join(view_folder, f"{view}.blade.php"), "w", encoding="utf-8") as f:
            f.write(form_view)


def append_routes(model_name, table):
    with open(ROUTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"Route::resource('{table}', App\Http\Controllers\Aspescu\{model_name}Controller::class);\n")

# Ejecutar todo
tables = parse_models()

for model_name, data in tables.items():
    table = data["table"]
    fields = data["fields"]

    generate_controller(model_name, table, fields)
    generate_service(model_name)
    generate_views(table, fields)
    append_routes(model_name, table)

print("✅ ¡Controladores, servicios, vistas y rutas generados exitosamente!")
