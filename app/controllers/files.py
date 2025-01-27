from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.brotes import Brote
from models.documento import Documento
from app import mysql
from werkzeug.utils import secure_filename
import os
from datetime import datetime

UPLOAD_FOLDER = 'uploads/documents/'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

brotes_bp = Blueprint('brotes_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@brotes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'folionotinmed': request.form['folionotinmed'].upper(),
            'brote': request.form['brote'],
            'fechanotificacion': request.form['fechanotificacion'],
            'casos': request.form['casos'],
            'fechacaptura': datetime.now().strftime('%Y-%m-%d'),
        }
        cursor = mysql.connection.cursor()
        Brote.create(cursor, data)
        brote_id = cursor.lastrowid  # Obtener el ID del nuevo brote

        # Manejo de documentos
        if 'documento' in request.files:
            file = request.files['documento']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                tipo_notificacion = request.form['tipo_notificacion']
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                doc_data = {
                    'brote_id': brote_id,
                    'nombre_archivo': filename,
                    'path': file_path,
                    'tipo_notificacion': tipo_notificacion,
                    'fecha_carga': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                }
                Documento.create(cursor, doc_data)

        mysql.connection.commit()
        flash('Brote registrado exitosamente', 'success')
        return redirect(url_for('brotes_bp.index'))

    return render_template('brotes/form.html', action="Registrar")

@brotes_bp.route('/edit/<int:brote_id>', methods=['GET', 'POST'])
def edit(brote_id):
    cursor = mysql.connection.cursor()
    brote = Brote.get_by_id(cursor, brote_id)
    if not brote:
        flash('Brote no encontrado', 'error')
        return redirect(url_for('brotes_bp.index'))

    if request.method == 'POST':
        data = {
            'folionotinmed': request.form['folionotinmed'].upper(),
            'brote': request.form['brote'],
            'fechanotificacion': request.form['fechanotificacion'],
            'casos': request.form['casos'],
            'fechacaptura': datetime.now().strftime('%Y-%m-%d'),
        }
        Brote.update(cursor, brote_id, data)

        # Manejo de documentos
        if 'documento' in request.files:
            file = request.files['documento']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                tipo_notificacion = request.form['tipo_notificacion']
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                doc_data = {
                    'brote_id': brote_id,
                    'nombre_archivo': filename,
                    'path': file_path,
                    'tipo_notificacion': tipo_notificacion,
                    'fecha_carga': datetime.now(),
                    'fecha_modificacion': datetime.now(),
                }
                Documento.create(cursor, doc_data)

        mysql.connection.commit()
        flash('Brote actualizado exitosamente', 'success')
        return redirect(url_for('brotes_bp.index'))

    documentos = Documento.get_by_brote_id(cursor, brote_id)
    return render_template('brotes/form.html', brote=brote, documentos=documentos, action="Editar")
