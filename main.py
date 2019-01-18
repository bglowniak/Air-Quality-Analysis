from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello CDC!"

# @app.route('/static/<path:path>')
# def static(path):
#     return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
