import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    """Main route that displays the Hello World page with name input"""
    name = None
    if request.method == 'POST':
        name = request.form.get('name')
    return render_template('index.html', name=name)

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    """Gallery page with image upload functionality"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Check if file is allowed and save it
        if file and file.filename and allowed_file(file.filename):
            # Type check to ensure filename is not None
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Image uploaded successfully!', 'success')
                return redirect(url_for('gallery'))
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files.', 'error')
    
    # Get list of uploaded images
    images = []
    if os.path.exists(UPLOAD_FOLDER):
        images = [f for f in os.listdir(UPLOAD_FOLDER) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(error)}")
    return "<h1>Internal Server Error</h1><p>Something went wrong on our end.</p>", 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        exit(1)