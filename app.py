import os
from flask import Flask, request, render_template, send_file
import rembg
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

OUTPUT_FOLDER = 'output'

def remove_background(input_path, output_folder):
    with open(input_path, 'rb') as input_file:
        input_image = input_file.read()

    output_image = rembg.remove(input_image)

    # Generate a unique output filename based on current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f'output_{timestamp}.png'
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, 'wb') as output_file:
        output_file.write(output_image)

    # Remove input image after processing
    os.remove(input_path)

    return output_filename

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', message='No selected file')

        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        output_filename = remove_background(file_path, OUTPUT_FOLDER)

        return render_template('result.html', filename=output_filename)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

def clear_output_folder():
    # Clear files older than 1 hour in the output folder
    threshold = datetime.now() - timedelta(hours=1)
    for file in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, file)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < threshold.timestamp():
            os.remove(file_path)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize scheduler for periodic output folder cleanup
    scheduler = BackgroundScheduler()
    scheduler.add_job(clear_output_folder, 'interval', hours=1)
    scheduler.start()

    app.run(debug=True)