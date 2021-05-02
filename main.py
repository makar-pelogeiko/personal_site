from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

class Works(db.Model):
    link_name = db.Column(db.String(120), nullable=False)
    title_name = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    img_path = db.Column(db.String(120), nullable=False)
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'{self.link_name}'
def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]

@app.route("/")
def index_page():
	return render_template('index.html', title_name='Макар')

@app.route("/works")
def my_works():
    projects = Works.query.filter().all()
    print(projects)
    print(len(projects))
    first = chunkify(projects, 2)[0]
    second = chunkify(projects, 2)[1]
    print(second)
    return render_template('works.html', projects_2=second, projects_1=first, title_name='Макар')

@app.route("/reviews")
def my_review():
    return redirect(url_for('index_page',_anchor='reviews', title_name='Макар'))

@app.route("/about-me")
def my_about_me():
    return redirect(url_for('index_page',_anchor='about-me', title_name='Макар'))

@app.route("/contact")
def my_contact():
    return render_template('contact.html', title_name='Контакты')

#@app.route("/<myWork>")
#def current_work(myWork):
#    return render_template('current_work.html', title_name=myWork.title_name, full_name=myWork.full_name, description=myWork.description)
#want to be like this

@app.route("/cwork", methods=('GET', 'POST'))
def cwork():
    if request.method == 'GET':
        try:
            mytitle=request.args.get('tname')
            work = Works.query.filter_by(title_name=mytitle).first()
            if work != None:
                return render_template('current_work.html', image_path=work.img_path, title_name=work.title_name, full_name=work.full_name, description=work.description)
        except SQLAlchemyError as e:
            print("error un cwork")
    return render_template('current_work.html', full_name='Not found')
	
if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
