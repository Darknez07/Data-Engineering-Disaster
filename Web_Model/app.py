from flask import Flask
from flask import render_template, request

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def router():
    if request.method == 'GET':
        return render_template('index.html', answer=False)
    else:
        try:
            val = int(request.form['dis'])
        except:
            val = 0
        print(val)
        return render_template('index.html', answer=True,num=val)

@app.route('/submit',methods=['POST','GET'])
def subs():
    if request.method == 'POST':
        print(request.json)
    return "<h1> Hey </h1>"

if __name__ == '__main__':
    app.run(debug=True)