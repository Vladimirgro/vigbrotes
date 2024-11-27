from flask import Blueprint, flash
from models.distritos import Distrito  # Asegúrate de que este import esté correcto

distritos_bp = Blueprint('distritos', __name__)

@distritos_bp.route('/distritos')
def obtener_distritos():
    try:
        distritos = Distrito.obtener_distritos()  # Obtener la lista de distritos
        return distritos  # Puedes retornar como JSON si es necesario
    except Exception as e:
        flash(f"Error al obtener distritos: {str(e)}")
        return [], 500  # Retorna una lista vacía en caso de error

