from flask import flash, Blueprint, render_template, request, redirect, url_for, abort, current_app
import os
from datetime import datetime
from models.distritos import Distrito
from models.brotes import Brote
from models.documento import Documento
from models.municipios import Municipio
from models.catalogos_diagnosticos import Diagnostico
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = current_app


brotes_bp = Blueprint('brotes_bp', __name__)

# Función para validar fechas
def validar_fechas(data):
    try:
        # Convertir fechas o asignar None si no están presentes
        fechas = {key: datetime.strptime(data[key], '%Y-%m-%d') if data.get(key) else None 
                  for key in ['fechinicio', 'fechnotifica', 'fechalta', 'fechaltanotin']}

        if fechas['fechnotifica'] and fechas['fechinicio'] and fechas['fechnotifica'] < fechas['fechinicio']:
            return 'La fecha de notificación debe ser mayor o igual que la fecha de inicio.'

        if fechas['fechalta'] and fechas['fechinicio'] and fechas['fechalta'] <= fechas['fechinicio']:
            return 'La fecha de alta debe ser mayor que la fecha de inicio.'
        
        if fechas['fechalta'] and fechas['fechnotifica'] and fechas['fechalta'] <= fechas['fechnotifica']:
            return 'La fecha de alta debe ser mayor que la fecha de notificación.'

        if fechas['fechaltanotin'] and fechas['fechalta'] and fechas['fechaltanotin'] < fechas['fechalta']:
            return 'La fecha de alta notinmed debe ser mayor o igual a la fecha de alta.'

    except ValueError:
        return 'Formato de fecha inválido. Asegúrate de que las fechas sean correctas.'

    return None

    
# Configura la ruta donde se guardarán los archivos subidos
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xlsx', 'xlsm', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def obtener_datos_formulario():
    return {
        'distritos': Distrito.obtener_distritos(),
        'municipios': Municipio.obtener_municipios(),
        'diagnosticos': Diagnostico.obtener_diagnosticos(),
    }


def validar_idbrote(idbrote):
    """Valida que el idbrote sea un entero."""
    try:
        return int(idbrote)
    except ValueError:
        flash('El ID del brote no es válido', 'danger')
        return None


def obtener_brote_por_id(idbrote):
    """Obtiene el brote por ID o muestra un error si no existe."""
    brote = Brote.get_by_id(idbrote)
    if not brote:
        flash("El brote no se encontró o no existe.", "danger")
    return brote


def recopilar_datos_formulario(form):
    """Recopila y transforma los datos del formulario para la base de datos."""
    return {
        'folionotinmed': form.get('folNotinmed', '').upper(),
        'fechnotinmed': form.get('fecNotnotinmed', '') or None,
        'tipoevento': form.get('evento', ''),
        'unidadnotif': form.get('unidad', '').upper(),
        'institucion': form.get('institucion', ''),
        'fechinicio': form.get('fechainicio', '') or None,
        'fechnotifica': form.get('fechanotifica', '') or None,
        'diagsospecha': form.get('diagsospecha', '').upper(),
        'jurisdiccion': form.get('juris', ''),
        'municipio': form.get('municipio', ''),
        'localidad': form.get('unilocalidaddad', '').upper(),
        'pobmascexp': form.get('pobmascexpuesta', ''),
        'pobfemexp': form.get('pobfemexpuesta', ''),
        'casosprob': form.get('probables', ''),
        'casosconf': form.get('confirmados', ''),
        'defunciones': form.get('defunciones', ''),
        'fechultimocaso': form.get('fecUcaso', '') or None,
        'fechalta': form.get('fechalta', '') or None,
        'resultado': form.get('resultado', '').upper(),
        'folioaltanotin': form.get('folAltaNoti', ''),
        'fechaltanotin': form.get('fecAltaNotinmed', '') or None,
        'nota': form.get('nota', '')
    }


def manejar_archivo(file, idbrote, tipo_notificacion):
    """Maneja la carga y registro de un archivo."""
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'brote_{idbrote}', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

            doc_data = {
                'brote_id': idbrote,
                'nombre_archivo': filename,
                'path': filepath,
                'tipo_notificacion': tipo_notificacion,
                'fechacarga': datetime.now(),
                'fechmodificacion': datetime.now()
            }
            Documento.update(**doc_data)
            flash('Documento actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al manejar el archivo: {str(e)}', 'danger')
            print(e)
    else:
        flash('Archivo no permitido o inválido', 'danger')


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
            'nota': request.form.get('nota', '')            
        })
        
        # Validación de las fechas ->  LAS VALIDACIONES NO FUNCIONAN
        error = validar_fechas(data)
        if error:
            flash(error, 'danger')
            return render_template('/vistas/register_brotes.html', **obtener_datos_formulario(), **data)
        
        
        # Validar si el 'folionotinmed' ya existe
        folio_a_buscar = data.get('folionotinmed')

        # Comprobar si el folio es nulo o vacío antes de buscar en la base de datos
        if folio_a_buscar:
            existing_brote = Brote.get_existing_brote(folio_a_buscar)
            if existing_brote:
                flash('El folio de notificación médica ya existe. Por favor, ingrese uno diferente.', 'danger')
                return render_template('/vistas/register_brotes.html', **obtener_datos_formulario(), **data)
                    

        # Obtener el ID del nuevo brote insertado                                                                      
        brote_id = Brote.create(**data)       
                    
        # Manejo de documentos
        if 'archivo' in request.files:
            file = request.files['archivo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                tipo_notificacion = request.form.get('tipo_notificacion')
                filepath = os.path.join(app.config['UPLOAD_FOLDER'],  f'brote_{brote_id}', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                doc_data = {
                    'brote_id': brote_id,
                    'nombre_archivo': filename,
                    'path': filepath,
                    'tipo_notificacion': tipo_notificacion,
                    'fechacarga': datetime.now(),
                    'fechmodificacion': datetime.now()
                }
                
                Documento.create(**doc_data)                
        
        flash('Brote registrado exitosamente', 'success')
        return redirect(url_for('brotes_bp.register_brotes'))                      
    
    
    return render_template('/vistas/register_brotes.html', **obtener_datos_formulario(), **data)


@brotes_bp.route('/lista_brotes', methods=['GET'])
def lista_brotes():
    # Consulta los brotes desde la base de datos
    brotes = Brote.obtener_todos()  # Obtiene todos los brotes
    return render_template('/vistas/listado_brotes.html', brotes=brotes)
    


@brotes_bp.route('/edit_brote/<int:idbrote>', methods=['GET', 'POST'], endpoint='edit_brote')
def edit_brote(idbrote):
    idbrote = validar_idbrote(idbrote)
    if idbrote is None:
        return redirect(url_for('brotes_bp.lista_brotes'))

    brote = obtener_brote_por_id(idbrote)
    if not brote:
        return redirect(url_for('brotes_bp.lista_brotes'))

    if request.method == 'POST':
        # Recopilar datos del formulario
        data = recopilar_datos_formulario(request.form)

        # Actualizar el brote
        try:
            Brote.update(idbrote, **data)
            flash('Brote actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el brote: {str(e)}', 'danger')
            return redirect(url_for('brotes_bp.edit_brote', idbrote=idbrote))

        # Manejo de archivos
        file = request.files.get('archivo')
        tipo_notificacion = request.form.get('tipo_notificacion', '')
        if file:
            manejar_archivo(file, idbrote, tipo_notificacion)

        return redirect(url_for('brotes_bp.edit_brote', idbrote=idbrote))

    return render_template('/vistas/edit_brotes.html', **obtener_datos_formulario(), brote=brote)



@brotes_bp.route('/files/<int:idbrote>')
def files(idbrote):
    try:
        # Verificar si el brote existe
        brote = Brote.get_by_id(idbrote)
        if not brote:
            flash("El brote no se encontró", "danger")
            return redirect(url_for('brotes_bp.lista_brotes'))
        
        # Obtener los documentos relacionados con el brote
        documentos = Documento.get_by_brote_id(idbrote)
        if not documentos:
            flash("No hay documentos asociados a este brote.", "info")
            documentos = []  # Asegúrate de que no sea None
        
        # Renderizar la plantilla con los documentos
        return render_template('/vistas/files.html', documentos=documentos, brote=brote)
    
    except Exception as e:        
        current_app.logger.error(f"Error en files: {e}")
        flash("Error al procesar la solicitud. Contacta al administrador.", "danger")
        return redirect(url_for('brotes_bp.lista_brotes'))
    
 
    
@brotes_bp.route('/files/download/<path:filepath>')
def descargar_archivo(filepath):
    try:
        # Reemplazar barras invertidas (\) por barras normales (/), si provienen de Windows
        normalized_path = filepath.replace('\\', '/')
        
        # Extraer la parte relativa desde 'static/uploads'
        upload_base = app.config['UPLOAD_FOLDER']
        if 'static/uploads/' in normalized_path:
            relative_path = normalized_path.split('static/uploads/')[-1]
        else:
            flash("Ruta de archivo no válida.", "danger")
            return redirect(url_for('brotes_bp.lista_brotes'))
        
        # Construir la ruta completa
        safe_path = os.path.join(upload_base, relative_path)
        
        # Verificar que el archivo exista
        if not os.path.isfile(safe_path):
            flash("El archivo no existe o no se encontró.", "danger")
            return redirect(url_for('brotes_bp.lista_brotes'))
        
        # Enviar el archivo como descarga
        return send_from_directory(upload_base, relative_path, as_attachment=True)
    except Exception as e:        
        flash("Error al descargar el archivo. Intenta nuevamente.", "danger")
        return redirect(url_for('brotes_bp.lista_brotes'))





