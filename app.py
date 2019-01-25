from flask import Flask, send_from_directory, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    Gets the index page
    """
    return render_template('index.html')




@app.route('/progress', methods=['GET'])
def progress():
    """
    Gets the progress page
    """
    return render_template('progress.html')




@app.route('/finish', methods=['GET'])
def finish():
    """
    Gets the finish page
    """
    return render_template('finish.html')




if __name__ == '__main__':
    app.run(debug=True)
