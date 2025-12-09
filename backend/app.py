from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from Video_analyser.pipeline import VideoAnalyzerPipeline
from generatorcode import AdvertisementGenerator, AdvertConfig
import tempfile
import logging
from flask import Flask, request, jsonify, send_file, Response
import requests
from werkzeug.utils import secure_filename
import mimetypes


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ad_server.log'),
        logging.StreamHandler()
    ]
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = './uploads'
GENERATED_FOLDER = './generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize the VideoAnalyzerPipeline
pipeline = VideoAnalyzerPipeline(api_key="AIzaSyDM1fL_EbWfkuJB18KRYjbe-PY-6E4aHak")

@app.route('/download-video/<path:video_url>')
def download_video(video_url):
    try:
        # Get the video through requests
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        # Get content type and filename
        content_type = response.headers.get('Content-Type', 'video/mp4')
        filename = video_url.split('/')[-1].split('?')[0]
        
        # Create generator to stream the video
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk

        # Return streaming response
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': content_type
        }
        
        return Response(
            generate(),
            headers=headers,
            content_type=content_type
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_video():
    try:
        # Retrieve form data
        product_name = request.form.get('productName')
        brand = request.form.get('brandName')
        tagline = request.form.get('tagline', '')
        color_palette = request.form.get('colorPalette', '')

        # Handle video file or URL
        video_path = ''
        if 'video_file' in request.files:
            video_file = request.files['video_file']
            if video_file.filename:
                filename = secure_filename(video_file.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(video_path)

        if not video_path:
            return jsonify({"error": "Please provide a video file."}), 400

        # Define product information
        product_info = {
            "product_name": product_name,
            "brand": brand,
            "tagline": tagline,
        }
        if color_palette:
            product_info["color_palette"] = color_palette

        # Run video analysis
        _, report_path = pipeline.analyze_video(video_path, product_info, sample_rate=30)

        # Read the contents of the generated text file
        with open(report_path, 'r') as report_file:
            report_content = report_file.read()

        return jsonify({"report": report_content}), 200

    except Exception as e:
        logging.error(f"Error in analyze_video: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error running analysis: {str(e)}"}), 500

@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        data = request.json
        config = AdvertConfig(
            product_name=data.get('productName'),
            tagline=data.get('tagline'),
            duration=int(data.get('duration', 8)),
            cta_text=data.get('callToAction'),
            logo_url=data.get('logoUrl'),
            target_audience=data.get('targetAudience'),
            campaign_goal=data.get('campaignGoal'),
            brand_palette=data.get('brandColors', '').split(',') if data.get('brandColors') else None,
            output_dir=app.config['GENERATED_FOLDER']
        )

        generator = AdvertisementGenerator(config)

        if generator.check_matching_criteria():
            result = generator.provide_preset_video()
            return jsonify({
                "status": "success",
                "type": "preset",
                "video_url": result['direct_url'],
                "filename": result['filename']
            }), 200

        # Generate new video
        logging.info("Generating new advertisement...")
        storyline = generator.generate_storyline()
        frame_info = generator.generate_frames(storyline)
        music_path = generator.generate_audio()
        output_path = generator.create_video(frame_info, music_path)

        return jsonify({
            "status": "success",
            "type": "generated",
            "video_url": f"http://localhost:5000/generated/{os.path.basename(output_path)}"
        }), 200

    except Exception as e:
        logging.error(f"Error in generate_video: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/generated/<filename>')
def generated_file(filename):
    file_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
    return send_file(
        file_path,
        mimetype='video/mp4',
        as_attachment=False,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)