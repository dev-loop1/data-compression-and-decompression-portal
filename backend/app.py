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
    
    start_time = time.time()
    
    try:
        if algorithm == 'rle':
            compressed_data = rle_compress(original_data)
            output_filename = f"{safe_filename}.rle"
        elif algorithm == 'huffman':
            compressed_data = huffman_compress(original_data)
            output_filename = f"{safe_filename}.huff"
        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        end_time = time.time()
        
        compressed_size = len(compressed_data)
        processing_time = (end_time - start_time) * 1000

        stats = {
            "originalSize": original_size,
            "compressedSize": compressed_size,
            "processingTime": round(processing_time, 2),
            "compressionRatio": round((1 - compressed_size / original_size) * 100, 2) if original_size > 0 else 0,
            "filename": output_filename 
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
        output_filename = ""
        
        if algorithm == 'rle':
            if not safe_filename.endswith('.rle'):
                 return jsonify({"error": "Invalid file: Expected a .rle extension."}), 400
            decompressed_data = rle_decompress(compressed_data)
            output_filename = safe_filename.rsplit('.rle', 1)[0]
        elif algorithm == 'huffman':
            if not safe_filename.endswith('.huff'):
                 return jsonify({"error": "Invalid file: Expected a .huff extension."}), 400
            decompressed_data = huffman_decompress(compressed_data)
            output_filename = safe_filename.rsplit('.huff', 1)[0]
        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        if not output_filename:
            output_filename = "decompressed_file"

        stats = {"filename": output_filename}

        response = send_file(
            io.BytesIO(decompressed_data),
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )
        response.headers['X-Compression-Stats'] = json.dumps(stats)

        return response

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during decompression. The file may be corrupt or of the wrong format. Details: {str(e)}"}), 500


# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)

