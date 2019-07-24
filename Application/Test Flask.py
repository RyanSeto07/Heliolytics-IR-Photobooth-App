from flask import Flask, escape, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('obtain_name'))


@app.route('/obtain', methods=['POST', 'GET'])
def obtain_name():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('display_name', name=user))
    else:
        user = request.args.get('nm')
        return redirect(url_for('display_name', name=user))



@app.route('/display/<name>')
def display_name(name):
    return 'Hi %s' % name


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)



