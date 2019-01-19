from flask import Flask, send_from_directory, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    Gets the index page
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
