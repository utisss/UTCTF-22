from flask import *
import pdfkit
import subprocess
import time
import os
import spwd
import crypt
from hmac import compare_digest as compare_hash
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        html_content = request.form.get('content')
        if html_content is None:
            return render_template('index.html')
        if '/environ' in html_content:
            # Don't let them read the flag from /proc/<pid>/environ
            return 'Aren''t you sneaky? That''s a good idea, but not the intended solution, so keep trying :)'

        # Filenames.
        html = render_template('document.html', content=html_content)
        uid = str(hash(time.time())) # Using a hash of the time ensures unique filenames between requests.
        out_filename = uid+'.pdf'
        html_filename = uid+'.html'
        html_file = open(html_filename, 'w')
        html_file.write(html)
        html_file.close()

        # Generate PDF.
        TIMEOUT = '3'
        subprocess.run(['xvfb-run', 'timeout', '--preserve-status', '-k', TIMEOUT, TIMEOUT,
                                    'wkhtmltopdf','--enable-local-file-access', html_filename, out_filename])
        
        # Cleanup and return result.
        out_file = open(out_filename, 'rb')
        output = out_file.read()
        out_file.close()
        #os.remove(out_filename)
        #os.remove(html_filename)
        response = make_response(output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=document.pdf'
        return response
    return render_template('index.html')

@app.route('/admin', methods=['POST','GET'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None:
            return render_template('login.html')

        # Check that username and password match a user in the system.
        try:
            pw1 = spwd.getspnam(username).sp_pwd
            pw2 = crypt.crypt(password, pw1)
            if compare_hash(pw2, pw1):
                return render_template('login.html', msg=os.environ['FLAG'])
            else:
                return render_template('login.html', msg='Incorrect password!')
        except KeyError: 
            # No such username.
            return render_template('login.html', msg='Incorrect username!')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')

