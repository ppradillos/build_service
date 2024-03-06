
'''
Author: Pablo Pradillos Do Carmo
email: pablo.pradillos@gmail.com

This web service will receive a URL of a git repository containing a simple 
C++ project with a CMakeLists.txt, and then it build it from source.

For such a thing, it will use the simplest way of building it, using CMake.

I have tested the service using cURL, Postman and Chrome. I have provided a little
front-end (pure HTML), in case you want to use it. BTW, in case you want to use the front-end, 
as I have not used any JavaScript, the index.html file assumes a hard coded IP address to find 
the server. Please, adapt it to make it work. 

Stuff implemented: 

Only HTTP and HTTPS URLs shall be allowed. It makes me easier
to test the service.

The server will check if the posted URL does exist, prior to starting the build process.

When it comes to clone the repo, it assumes no sign onto the ScM service (Github, BitBucket, etc.)
is required. If so, the server will throw an error.

Cloned repo shall be cleared after building the project, so successive request will not fail due to
"not empty directory" error.

Stuff not implemented for the sake of simplicity, but I would implement if this code would go to production:
    - HTTPS support:    I didn't want to mess with TLS certificates, that it would make the test phase longer
    - SSH support:      I'm fully aware that accessing git repos via SSH is common. But such a thing would require to add
                        extra parameters (passphrase, public key) to the POST request, and processing them.
    - Responsiveness against heavy loads:   For sure, this web server would break in case of heavy workloads. But I didn't find
                        necessary to focus any energy on it, as this is not an e-commerce application.
                        
URLs tested:
    - One repo of mine: https://github.com/ppradillos/log4embedded.git
    - One repo whose author I know nothing about:   https://github.com/flier/zipkin-cpp.git

'''


import os
import shutil
import server_utils
from flask import Flask, request, send_file, render_template, jsonify

app = Flask(__name__)

# Handle GET requests for the root URL
@app.route('/')
def index():
    return render_template('index.html')

# Handle POST requests for the '/build' endpoint
@app.route('/build', methods=['POST'])
def build_project():
    try:
        # Get the Git repository URL from the POST request
        repo_url = request.form.get('repo_url')
        
        # Check if the URL exists
        if not server_utils.check_url_exists(repo_url):
            return jsonify({'error': 'Provided URL does not exist or it is not supported.'}), 404

        # Clone the Git repository
        repo_dir = '/tmp/build_repo'
        
        if not server_utils.clone_repository(repo_url, repo_dir):
            return jsonify({'error': 'Error at cloning the repository. Timeout.'}), 404

        # Change directory to the repository
        os.chdir(repo_dir)

        # Create a build directory
        build_dir = '/tmp/build_result'
        os.makedirs(build_dir, exist_ok=True)
        
        # Create a name for the resulting build output and ZIP file
        output_dir = '/tmp/build_output'
        zip_file_path = output_dir + '.zip'

        # Run CMake to build the project
        os.system(f'cmake -B{build_dir} .')
        os.system(f'cmake --build {build_dir}')

        # Create a zip file with the build result
        shutil.make_archive(output_dir, 'zip', build_dir)
        
        # Clean up: Clear the build directory and cloned repository
        server_utils.clear_folder(build_dir)
        server_utils.clear_folder(repo_dir)

        # Return the zip file to the user
        return send_file(zip_file_path, as_attachment=True)        

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    print("Starting the build server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
