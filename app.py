import os
import openai
from flask import Flask, request, render_template, send_file
from pdfminer.high_level import extract_text
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Ask the user for the OpenAI API key at the start
openai.api_key = input("Please enter your OpenAI API key: ")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Check if the file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from the PDF
def extract_pdf_text(pdf_file):
    return extract_text(pdf_file)

# Generate HTML resume from extracted text using OpenAI
def generate_html_resume(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that formats resumes into a clean, structured HTML format."},
            {"role": "user", "content": f"Convert the following resume into HTML: {text}"}
        ]
    )
    # Return the HTML formatted resume
    return response['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400

        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)

            # Extract text from the PDF
            text = extract_pdf_text(filename)

            # Generate HTML resume
            html_resume = generate_html_resume(text)

            # Save the HTML output
            output_filename = "resume.html"
            with open(output_filename, "w") as f:
                f.write(html_resume)

            # Send the file to the client
            return send_file(output_filename, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 