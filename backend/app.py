import os
import io
import time
import json
import traceback
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from algorithms.rle import rle_compress, rle_decompress
from algorithms.huffman import huffman_compress, huffman_decompress

# --- Flask App Initialization ---
app = Flask(__name__)

CORS(app, expose_headers=['Content-Disposition', 'X-Compression-Stats'])

# --- API Endpoints ---

@app.route('/api/compress', methods=['POST'])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    algorithm = request.form.get('algorithm')

    if file.filename == '' or not algorithm:
        return jsonify({"error": "Missing file or algorithm selection"}), 400

    original_data = file.read()
    original_size = len(original_data)
    
    safe_filename = secure_filename(file.filename)
    base_name, original_ext = os.path.splitext(safe_filename)
    
    start_time = time.time()
    
    try:
        if algorithm == 'rle':
            compressed_data = rle_compress(original_data)
        elif algorithm == 'huffman':
            compressed_data = huffman_compress(original_data)
        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        output_filename = f"{base_name}_compressed_{algorithm}{original_ext}"

        end_time = time.time()
        
        compressed_size = len(compressed_data)
        processing_time = (end_time - start_time) * 1000

        stats = {
            "originalSize": original_size,
            "compressedSize": compressed_size,
            "processingTime": round(processing_time, 2),
            "compressionRatio": round((1 - compressed_size / original_size) * 100, 2) if original_size > 0 else 0
        }
        
        response = send_file(
            io.BytesIO(compressed_data),
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )
        response.headers['X-Compression-Stats'] = json.dumps(stats)
        
        return response

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during compression: {str(e)}"}), 500


@app.route('/api/decompress', methods=['POST'])
def decompress_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    algorithm = request.form.get('algorithm')

    if file.filename == '' or not algorithm:
        return jsonify({"error": "Missing file or algorithm selection"}), 400

    compressed_data = file.read()
    safe_filename = secure_filename(file.filename)
    
    try:
        output_filename = safe_filename.replace(f"_compressed_{algorithm}", "")
        
        if algorithm == 'rle':
            decompressed_data = rle_decompress(compressed_data)
        elif algorithm == 'huffman':
            decompressed_data = huffman_decompress(compressed_data)
        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        return send_file(
            io.BytesIO(decompressed_data),
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during decompression. The file may be corrupt or of the wrong format. Details: {str(e)}"}), 500


# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)

