from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image
import io
import os

app = Flask(__name__)

# Function to encode message into image
def encode_message(image, message):
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    data_index = 0
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if data_index < len(binary_message):
                # Modify the least significant bit of the red channel
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1
            pixels[x, y] = (r, g, b)

            if data_index >= len(binary_message):
                return image

# Function to decode message from image
def decode_message(image):
    binary_message = ""
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_message += str(r & 1)
            if len(binary_message) % 8 == 0 and len(binary_message) >= 8:
                byte = binary_message[-8:]
                if byte == "00000000":  # Null terminator
                    return ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message)-8, 8))

    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files or 'message' not in request.form:
        return redirect(url_for('index'))

    image_file = request.files['image']
    message = request.form['message']

    # Open the image
    image = Image.open(image_file)
    encoded_image = encode_message(image, message + "\0")  # Add null terminator

    # Save the encoded image to a bytes buffer
    buffer = io.BytesIO()
    encoded_image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='encoded_image.png')

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image_file = request.files['image']

    # Open the image
    image = Image.open(image_file)
    decoded_message = decode_message(image)

    return render_template('index.html', decoded_message=decoded_message)

if __name__ == '__main__':
    app.run(debug=True)