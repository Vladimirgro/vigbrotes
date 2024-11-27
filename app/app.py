from flask import Flask, render_template, flash
from controllers.brotes_controller import brotes_bp
from controllers.distritos_controller import distritos_bp
from controllers.municipios_controller import municipios_bp
from controllers.catalogos_controller import catalogo_brotes_bp
from config import Config
from datetime import datetime

app = Flask(__name__)

app.config.from_object(Config)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        flash(f"Error al cargar la página: {str(e)}")
        return render_template('error.html'), 500  # Asegúrate de tener un template 'erro ME FALTA CREAR

# Registro del blueprint del controlador
app.register_blueprint(brotes_bp)

app.register_blueprint(distritos_bp)

app.register_blueprint(municipios_bp)

app.register_blueprint(catalogo_brotes_bp)

@app.template_filter('format_date')
def format_date(value):
    try:
        # Si el valor ya es un objeto datetime
        if isinstance(value, datetime):
            return value.strftime('%d/%m/%Y')
        # Si el valor es una cadena
        elif isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y')
        return ""  # Si el valor es None u otro tipo
    except (ValueError, TypeError):
        return "Fecha no válida"


if __name__ == '__main__':
    app.run(debug=True)
