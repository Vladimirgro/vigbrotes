from flask import flash, Blueprint, render_template, request, redirect, url_for, jsonify, current_app
import os
from datetime import datetime
from models.distritos import Distrito
from models.brotes import Brote
from models.municipios import Municipio
from models.catalogos_diagnosticos import Diagnostico
from werkzeug.utils import secure_filename

app = current_app


brotes_bp = Blueprint('brotes_bp', __name__)
    
# Configura la ruta donde se guardarán los archivos subidos
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@brotes_bp.route('/brotes', methods=['GET'])
def brotes():
    return render_template('/vistas/brotes.html')

@brotes_bp.route('/register_brotes', methods=['GET', 'POST']) # Ruta para mostrar el formulario de registro de brotes
def register_brotes():
    # Inicializar el diccionario de datos para el formulario
    data = {
        'folionotinmed': '',
        'fechnotinmed': None,
        'tipoevento': '',
        'unidadnotif': '',
        'institucion': '',
        'fechinicio': None,
        'fechnotifica': None,
        'diagsospecha': '',
        'jurisdiccion': '',
        'municipio': '',
        'localidad': '',
        'pobmascexp': '',
        'pobfemexp': '',
        'casosprob': '',
        'casosconf': '',
        'defunciones': '',
        'fechultimocaso': None,
        'fechalta': None,
        'resultado': '',
        'folioaltanotin': '',
        'fechaltanotin': None,
        'nota': '',        
    }

    if request.method == 'POST':  # Obtener los datos del formulario
        # Asignar datos del formulario a 'data'
        data.update({
            'folionotinmed': request.form.get('folNotinmed', '').upper(),
            'fechnotinmed': request.form.get('fecNotnotinmed', '') or None,
            'tipoevento': request.form.get('evento', ''),
            'unidadnotif': request.form.get('unidad', '').upper(),
            'institucion': request.form.get('institucion', ''),
            'fechinicio': request.form.get('fechainicio', '') or None,
            'fechnotifica': request.form.get('fechanotifica', '') or None,
            'diagsospecha': request.form.get('diagsospecha', '').upper(),
            'jurisdiccion': request.form.get('juris', ''),
            'municipio': request.form.get('municipio', ''),
            'localidad': request.form.get('unilocalidaddad', '').upper(),
            'pobmascexp': request.form.get('pobmascexpuesta', ''),
            'pobfemexp': request.form.get('pobfemexpuesta', ''),
            'casosprob': request.form.get('probables', ''),
            'casosconf': request.form.get('confirmados', ''),
            'defunciones': request.form.get('defunciones', ''),
            'fechultimocaso': request.form.get('fecUcaso', '') or None,
            'fechalta': request.form.get('fechalta', '') or None,
            'resultado': request.form.get('resultado', '').upper(),
            'folioaltanotin': request.form.get('folAltaNoti', ''),
            'fechaltanotin': request.form.get('fecAltaNotinmed', '') or None,
            'nota': request.form.get('nota', ''),
            'documento': request.form.get('documento', '')
        })     
            # Manejar el archivo subido
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
            
        file = request.files['archivo']
            
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])            
            
            filename = secure_filename(file.filename)                                    
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['archivo'] = filename           
            
        # Validar si el 'folionotinmed' ya existe
        folio_a_buscar = data['folionotinmed']
        print(folio_a_buscar)
        existing_brote = Brote.get_existing_brote(folio_a_buscar)
        if existing_brote:
            flash('El folio de notificación médica ya existe. Por favor, ingrese uno diferente.', 'danger')
            return render_template('/vistas/register_brotes.html', 
                                   distritos=Distrito.obtener_distritos(), 
                                   municipios=Municipio.obtener_municipios(), 
                                   diagnosticos=Diagnostico.obtener_diagnosticos(), **data)
            
        # Inicializar fechas a None
        fecha_inicio = None
        fecha_notifica = None
        fecha_alta = None
        fecha_alta_notinmed = None
        
        # Debug: Imprimir los datos recibidos
        print("Datos recibidos:", data)
        
        # Validación de las fechas
        try:
            if data['fechinicio']:
                fecha_inicio = datetime.strptime(data['fechinicio'], '%Y-%m-%d')  if data['fechinicio'] else None
            if data['fechnotifica']:
                fecha_notifica = datetime.strptime(data['fechnotifica'], '%Y-%m-%d')  if data['fechnotifica'] else None
            if data['fechalta']:
                fecha_alta = datetime.strptime(data['fechalta'], '%Y-%m-%d') if data['fechalta'] else None
            if data['fechaltanotin']:
                fecha_alta_notinmed = datetime.strptime(data['fechaltanotin'], '%Y-%m-%d') if data['fechaltanotin'] else None

            # Validaciones
            if fecha_notifica < fecha_inicio:
                flash('La fecha de notificación debe ser mayor o igual que la fecha de inicio.', 'danger')
                return render_template('/vistas/register_brotes.html', distritos=Distrito.obtener_distritos(), municipios=Municipio.obtener_municipios(), diagnosticos=Diagnostico.obtener_diagnosticos(), **data)

            if fecha_alta and (fecha_alta <= fecha_inicio or fecha_alta <= fecha_notifica):
                flash('La fecha de alta debe ser mayor que la fecha de inicio y la fecha de notificación.', 'danger')
                return render_template('/vistas/register_brotes.html', distritos=Distrito.obtener_distritos(), municipios=Municipio.obtener_municipios(), diagnosticos=Diagnostico.obtener_diagnosticos(), **data)

            if fecha_alta_notinmed and fecha_alta and fecha_alta_notinmed < fecha_alta:
                flash('La fecha de alta notinmed debe ser mayor o igual a la fecha de alta.', 'danger')
                return render_template('/vistas/register_brotes.html', distritos=Distrito.obtener_distritos(), municipios=Municipio.obtener_municipios(), diagnosticos=Diagnostico.obtener_diagnosticos(), **data)

        except ValueError as e:
            flash('Formato de fecha inválido. Asegúrate de que las fechas sean correctas.', 'danger')
            print("Error de formato de fecha:", e)
            return render_template('/vistas/register_brotes.html', distritos=Distrito.obtener_distritos(), municipios=Municipio.obtener_municipios(), diagnosticos=Diagnostico.obtener_diagnosticos(), **data)

        # Si todas las validaciones son exitosas, crear un nuevo brote en la base de datos
        try:
            Brote.create(**data)
            flash('Brote registrado exitosamente', 'success')
            return redirect(url_for('brotes_bp.register_brotes'))
        except Exception as e:
            flash(f'Error al registrar el brote: {str(e)}', 'danger')
            return render_template('/vistas/register_brotes.html', distritos=Distrito.obtener_distritos(), municipios=Municipio.obtener_municipios(), diagnosticos=Diagnostico.obtener_diagnosticos(), **data)
    
    distritos = Distrito.obtener_distritos()  # Obtener distritos para mostrar en el formulario
    municipios = Municipio.obtener_municipios() # Obtener municipios para mostrar en el formulario
    diagnosticos = Diagnostico.obtener_diagnosticos()
    
    return render_template('/vistas/register_brotes.html', distritos=distritos, municipios=municipios, diagnosticos=diagnosticos, **data)


@brotes_bp.route('/lista_brotes', methods=['GET'])
def lista_brotes():
    # Consulta los brotes desde la base de datos
    brotes = Brote.obtener_todos()  # Obtiene todos los brotes
    return render_template('/vistas/listado_brotes.html', brotes=brotes)
    


@brotes_bp.route('/edit_brote/<int:idbrote>', methods=['GET', 'POST'])
def edit_brote(idbrote):
    try:
        idbrote = int(idbrote)  # Asegúrate de que sea un número entero
    except ValueError:
        flash('El ID del brote no es válido', 'danger')  # Mensaje si el valor no es válido
        return redirect(url_for('brotes_bp.lista_brotes'))  # Redirigir al listado de brotes   
                
    brote = Brote.get_by_id(idbrote)
    
    if not brote:
        flash("El brote no se encontró o no existe.", "danger")
        return redirect(url_for('brotes_bp.lista_brotes'))
    
    if request.method == 'POST':
        data = {
            'folionotinmed': request.form.get('folNotinmed', '').upper(),
            'fechnotinmed': request.form.get('fecNotnotinmed', '') or None,
            'tipoevento': request.form.get('evento', ''),
            'unidadnotif': request.form.get('unidad', '').upper(),
            'institucion': request.form.get('institucion', ''),
            'fechinicio': request.form.get('fechainicio', '') or None,
            'fechnotifica': request.form.get('fechanotifica', '') or None,
            'diagsospecha': request.form.get('diagsospecha', '').upper(),
            'jurisdiccion': request.form.get('juris', ''),
            'municipio': request.form.get('municipio', ''),
            'localidad': request.form.get('unilocalidaddad', '').upper(),
            'pobmascexp': request.form.get('pobmascexpuesta', ''),
            'pobfemexp': request.form.get('pobfemexpuesta', ''),
            'casosprob': request.form.get('probables', ''),
            'casosconf': request.form.get('confirmados', ''),
            'defunciones': request.form.get('defunciones', ''),
            'fechultimocaso': request.form.get('fecUcaso', '') or None,
            'fechalta': request.form.get('fechalta', '') or None,
            'resultado': request.form.get('resultado', '').upper(),
            'folioaltanotin': request.form.get('folAltaNoti', ''),
            'fechaltanotin': request.form.get('fecAltaNotinmed', '') or None,
            'nota': request.form.get('nota', ''),
            'documento': request.form.get('documento', '')
        }

        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
            
        file = request.files['archivo']
            
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['archivo'] = filename  # Guarda el nombre del archivo en los datos del formulario

        # Validación y actualización
        try:
            Brote.update(idbrote, **data)
            flash('Brote actualizado exitosamente', 'success')
            return redirect(url_for('brotes_bp.lista_brotes'))  # Redirige después de la actualización exitosa
        except Exception as e:
            flash(f'Error al actualizar el brote: {str(e)}', 'danger')
            print(e)
    distritos = Distrito.obtener_distritos()  # Obtener distritos para mostrar en el formulario
    municipios = Municipio.obtener_municipios() # Obtener municipios para mostrar en el formulario
    diagnosticos = Diagnostico.obtener_diagnosticos()

    return render_template('/vistas/edit_brotes.html', distritos=distritos, municipios=municipios, diagnosticos=diagnosticos, brote=brote)

@brotes_bp.route('/files', methods=['GET'])
def files():    
    return render_template('/vistas/files.html')

