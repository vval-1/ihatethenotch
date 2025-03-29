import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = 'static/files'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}
BLACK_BAR_HEIGHT = 74

MACBOOK_WIDTH = 3024
MACBOOK_HEIGHT = 1964

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        file = request.files.get('uploaded_file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            processed_filename = f"processed_{filename}"
            processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            
            file.save(upload_filepath)
            try:
                with Image.open(upload_filepath) as img:
                    img_ratio = img.width / img.height
                    macbook_ratio = MACBOOK_WIDTH / (MACBOOK_HEIGHT - BLACK_BAR_HEIGHT)
                    
                    if img_ratio > macbook_ratio:
                        new_height = MACBOOK_HEIGHT - BLACK_BAR_HEIGHT
                        new_width = int(new_height * img_ratio)
                        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                        left = (resized_img.width - MACBOOK_WIDTH) // 2
                        right = left + MACBOOK_WIDTH
                        resized_img = resized_img.crop((left, 0, right, new_height))
                    else:
                        new_width = MACBOOK_WIDTH
                        new_height = int(new_width / img_ratio)
                        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                        top = (resized_img.height - (MACBOOK_HEIGHT - BLACK_BAR_HEIGHT)) // 2
                        bottom = top + (MACBOOK_HEIGHT - BLACK_BAR_HEIGHT)
                        resized_img = resized_img.crop((0, top, new_width, bottom))
                    
                    final_img = Image.new('RGB', (MACBOOK_WIDTH, MACBOOK_HEIGHT), color=(0, 0, 0))
                    final_img.paste(resized_img, (0, BLACK_BAR_HEIGHT))
                    
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        final_img.save(processed_filepath, format='JPEG', quality=100)
                    else:
                        final_img.save(processed_filepath, format='PNG')
                
                return redirect(url_for('download_file', filename=processed_filename))
            except Exception as e:
                return f"Error processing image: {e}"
        else:
            return "Invalid file."
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)