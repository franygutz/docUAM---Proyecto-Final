# ================================================================
# 1. IMPORTS
# ================================================================
import os
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from models import db, Document, User, Comment 
from functools import wraps
from datetime import datetime

from utils.pdf import extract_pdf_metadata
from utils.docx import extract_docx_metadata
from utils.pptx import extract_pptx_metadata
from tree import *
from utils.documentpy import *

# ================================================================
# 2. CONFIGURACIÓN DE LA APLICACIÓN
# ================================================================
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'esta-es-una-clave-muy-secreta-cambiala'
db.init_app(app)

with app.app_context():
    db.create_all()

# ================================================================
# 3. FUNCIONES DE AYUDA Y SEGURIDAD
# ================================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while Document.query.filter_by(filename=new_filename).first():
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ================================================================
# 4. RUTAS DE AUTENTICACIÓN
# ================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash(f'¡Bienvenido de nuevo, {user.email}!', 'success')
            return redirect(url_for('home'))
        flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'error')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

# ================================================================
# 5. RUTAS PRINCIPALES
# ================================================================

@app.route('/')
@login_required
def home():
    recent_docs = Document.query.filter_by(user_id=session['user_id']).order_by(Document.created_at.desc()).limit(5).all()
    return render_template('home.html', docs=recent_docs)

@app.route('/my-files')
@login_required
def my_files():
    sort_by = request.args.get('sort_by', 'title')
    sort_dir = request.args.get('sort_dir', 'asc')
    search_query = request.args.get('search', '')
    query = Document.query.filter_by(user_id=session['user_id'])
    if search_query:
        query = query.filter(Document.title.ilike(f'%{search_query}%'))
    docs_all = query.all()
    def get_sort_key(doc):
        value = getattr(doc, sort_by)
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value).lower()
    tree = ArbolBinario()
    if docs_all:
        for doc in docs_all:
            tree.insertar(Nodo(DocumentKey(doc, key_func=get_sort_key)))
    sorted_docs = tree.inorden()
    if sort_dir == 'desc':
        sorted_docs.reverse()
    return render_template('my_files.html', docs=sorted_docs, sort_by=sort_by, sort_dir=sort_dir, search_query=search_query)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No se encontró el campo del archivo.', 'error')
        return redirect(url_for('my_files'))
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo.', 'warning')
        return redirect(url_for('my_files'))
    if not allowed_file(file.filename):
        flash('Tipo de archivo no permitido.', 'error')
        return redirect(url_for('my_files'))
    filename = secure_filename(file.filename)
    unique_filename = get_unique_filename(filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(save_path)
    ext = unique_filename.rsplit('.', 1)[1].lower()
    meta = {}
    if ext == 'pdf': meta = extract_pdf_metadata(save_path)
    elif ext == 'docx': meta = extract_docx_metadata(save_path)
    elif ext in ('ppt', 'pptx'): meta = extract_pptx_metadata(save_path)
    doc = Document(
        title=meta.get('title') or unique_filename,
        author=meta.get('author'),
        created_at=meta.get('created_at') or datetime.utcnow(),
        filename=unique_filename,
        user_id=session['user_id']
    )
    db.session.add(doc)
    db.session.commit()
    flash(f'¡Archivo "{unique_filename}" subido con éxito!', 'success')
    return redirect(url_for('my_files'))

# ================================================================
# 6. RUTAS PARA DOCUMENTOS INDIVIDUALES
# ================================================================

@app.route('/document/<int:doc_id>')
@login_required
def document_detail(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        abort(403)
    return render_template('document_detail.html', doc=doc)

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    doc = Document.query.filter_by(filename=filename, user_id=session['user_id']).first_or_404()
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# --- ESTA ES LA RUTA QUE FALTABA EN TU ARCHIVO ---
@app.route('/document/<int:doc_id>/edit', methods=['POST'])
@login_required
def edit_properties(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        abort(403)
    
    doc.title = request.form.get('title', doc.title)
    doc.author = request.form.get('author', doc.author)
    
    db.session.commit()
    flash('Propiedades del documento actualizadas con éxito.', 'success')
    return redirect(url_for('document_detail', doc_id=doc.id))


@app.route('/document/<int:doc_id>/save_note', methods=['POST'])
@login_required
def save_note(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        abort(403)
    doc.notes = request.form['notes']
    db.session.commit()
    flash('¡Nota guardada con éxito!', 'success')
    return redirect(url_for('document_detail', doc_id=doc.id))

@app.route('/document/<int:doc_id>/add_comment', methods=['POST'])
@login_required
def add_comment(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        abort(403)
    comment_content = request.form['comment']
    if comment_content:
        new_comment = Comment(content=comment_content, document_id=doc.id, user_id=session['user_id'])
        db.session.add(new_comment)
        db.session.commit()
        flash('Comentario añadido.', 'success')
    return redirect(url_for('document_detail', doc_id=doc.id))

@app.route('/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        abort(403)
    try:
        filename_to_delete = doc.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_to_delete)
        if os.path.exists(filepath):
            os.remove(filepath)
        db.session.delete(doc)
        db.session.commit()
        flash(f'Archivo "{filename_to_delete}" eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el archivo: {e}', 'error')
    return redirect(url_for('my_files'))

# ================================================================
# 7. INICIAR LA APLICACIÓN
# ================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
