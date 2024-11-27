from flask import Blueprint, flash
from models.municipios import Municipio  # Asegúrate de que este import esté correcto

municipios_bp = Blueprint('municipios', __name__)

@municipios_bp.route('/municipios')
def obtener_municipios():
    try:
        municipios = Municipio.obtener_municipios()  # Obtener la lista de distritos
        return municipios  # Puedes retornar como JSON si es necesario
    except Exception as e:
        flash(f"Error al obtener distritos: {str(e)}")
        return [], 500  # Retorna una lista vacía en caso de error