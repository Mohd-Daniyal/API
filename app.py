from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
from resume_to_text import convert_pdf_to_text
from generate_email import generate_email
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Update this with your actual Netlify app URL
cors = CORS(app, resources={r"/upload-resume": {"origins": "https://coldcraft.netlify.app/"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/upload-resume', methods=['POST'])
@cross_origin(origin='https://coldcraft.netlify.app/')
def upload_resume():
    try:
        email_id = request.form.get('email_id')
        resume_file = request.files['resume']
        company_name = request.form.get('company_name')

        if not email_id or not resume_file or not company_name:
            return jsonify({'message': 'Missing required parameters'}), 400

        resume_directory = '/tmp/generations'
        os.makedirs(resume_directory, exist_ok=True)
        resume_path = os.path.join(resume_directory, f"{email_id}_resume.pdf")

        # Save the resume file
        resume_file.save(resume_path)
        convert_pdf_to_text(resume_path)

        generated_email = generate_email(email_id, "", company_name)

        # Clean up the temporary files
        for filename in os.listdir(resume_directory):
            file_path = os.path.join(resume_directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify({'message': 'Resume uploaded successfully', 'generated_email': generated_email}), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
