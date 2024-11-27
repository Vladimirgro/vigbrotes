from flask import Blueprint, request, render_template, jsonify
from models.catalogos_diagnosticos import Diagnostico  # Asegúrate de que este import esté correcto

catalogo_brotes_bp = Blueprint('catalogo_brotes', __name__)

@catalogo_brotes_bp.route('/register_catalogo', methods=['GET', 'POST'])
def register_catalogo():
    if request.method == 'POST':
        # Obtén los datos del formulario
        diagnostico = request.json.get('diagnostico_cat').upper()  # Cambia esto a request.json
        periodoIncubacion = request.json.get('incubacion_cat')
        
        # Verificar que los campos no estén vacíos
        if not diagnostico or not periodoIncubacion:
            return jsonify({"message": "Todos los campos son obligatorios.", "category": "error"}), 400

        try:
            # Crear un nuevo diagnóstico en la base de datos
            Diagnostico.create(diagnostico, periodoIncubacion)            
            return jsonify({"message": "Diagnóstico registrado exitosamente", "category": "success"}), 200
        except Exception as e:
            return jsonify({"message": f"Error al registrar el diagnóstico: {str(e)}", "category": "error"}), 500
    
    # Obtener los diagnósticos para mostrarlos en el template en una solicitud GET
    # diagnosticos = Diagnostico.obtener_diagnosticos()
    return render_template('/vistas/catalogo_brotes.html')

@catalogo_brotes_bp.route('/lista_diagnostico')
def lista_diagnostico():
    diagnosticos = Diagnostico.obtener_diagnosticos()  # Obtiene todos los registros        
    return jsonify(diagnosticos)
    # return render_template('/vistas/catalogo_brotes.html', diagnosticos=diagnosticos)


# Ruta para actualizar los datos del diagnóstico
@catalogo_brotes_bp.route('/actualizar_diagnostico/<int:id>', methods=['POST'])
def actualizar_diagnostico(id):
    data = request.json
    diagnostico = data.get('edit_diagnostico').upper()
    periodo_incubacion = data.get('edit_periodoIncubacion')

    if not diagnostico or not periodo_incubacion:
        return jsonify({"message": "Todos los campos son obligatorios."}), 400

    try:
        Diagnostico.actualizar(id, diagnostico, periodo_incubacion)
        return jsonify({"message": "Diagnóstico actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"message": f"Error al actualizar el diagnóstico: {str(e)}"}), 500
    

@catalogo_brotes_bp.route('/editar_diagnostico/<int:id>', methods=['GET'])
def editar_diagnostico(id):
    # Lógica para obtener el diagnóstico por ID y devolverlo como JSON
    diagnostico = Diagnostico.obtener_por_id(id)
    if not diagnostico:
        return jsonify({"message": "Diagnóstico no encontrado"}), 404
    return jsonify({        
        "edit_diagnostico": diagnostico.diagnostico,
        "edit_periodoIncubacion": diagnostico.periodoIncubacion
    }), 200
