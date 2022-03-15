from flask import *
import os, io, base64
from PIL import Image, ImageDraw, ImageFont
from encrypted_session import EncryptedSessionInterface

from Crypto.Random import get_random_bytes, random
key1 = get_random_bytes(32)
key2 = get_random_bytes(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = key1
app.config['SESSION_CRYPTO_KEY'] = key2

app.session_interface = EncryptedSessionInterface()

FLAG = os.environ.get("FLAG")
NUM_TO_SOLVE = int(os.environ.get("NUM_TO_SOLVE"))

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def gen_challenge():
    return ''.join([random.choice(chars) for _ in range(6)])

def gen_img(challenge):
    mask = Image.open('mask.png')

    img = Image.new("RGB", (500, 150), color=(0, 0, 0))
    fnt = ImageFont.truetype("Arial.ttf", 100)
    d = ImageDraw.Draw(img)
    d.text((10, 10), challenge, font=fnt, fill=(255, 255, 255))

    # XOR mask and img together
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = img.getpixel((i, j))
            a, b, c = mask.getpixel((i , j))
            img.putpixel((i, j), (r ^ a, g ^ b, b ^ c))

    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    
    return base64.b64encode(imgByteArr).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'count' not in session:
        session['count'] = 0
        session['challenge'] = gen_challenge()
    
    if session['count'] >= NUM_TO_SOLVE:
        return FLAG
    
    soln = request.form.get("solution")
    if soln is not None:
        if soln == session['challenge']:
            session['count'] += 1
            if session['count'] >= NUM_TO_SOLVE:
                return FLAG
        else:
            session['count'] = 0
        
        session['challenge'] = gen_challenge()

    resp = make_response(render_template('index.html', count=session['count'], challenge=gen_img(session['challenge'])))
    return resp

if __name__ == '__main__':
    app.run(debug=True)
