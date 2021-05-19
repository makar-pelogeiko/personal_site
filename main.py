from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
import json
import requests

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = '8c6e8548b98042456995b42d1165d63e943cdf8554425452224073287d529d9b8938ea0f01eabed9'
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

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vk_id = db.Column(db.String(255), unique=True, nullable=True)
    vk_access_token = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'User: {self.name}\n' \
               f'ID: {self.id}\n' \
               f'VK ID: {self.vk_id}\n' \
               f'Posted time: {self.vk_access_token}\n' \
               f'Time: {self.timestamp}\n' \

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

#@app.route("/contact")
#def my_contact():
#    return render_template('contact.html', title_name='Контакты')

@app.route("/contact")
def my_contact():
    if not session.get('user_id') is None:
        # posts = Posts.query.all()
        user_id = session.get('user_id')
        user = Users.query.filter_by(id=user_id).first()
        return render_template("logout_index.html", name=user.name, vkuser=user_id)
    #session['user_id'] = 'dsddd'
    return render_template('contact.html', title_name='Контакты')

#@app.route("/")
#def main_page():
#    if not session.get('user_id') is None:
        # posts = Posts.query.all()
#        user_id = session.get('user_id')
#        user = Users.query.filter_by(id=user_id).first()
#        return render_template("logout_index.html", name=user.name)
#    return render_template('login_index.html')

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
#############################
@app.route("/logout")
def logout():
    if not session.get('user_id'):
        return redirect(url_for('my_contact'))
    session.pop('user_id', None)
    return redirect(url_for('my_contact'))


@app.route("/vk_login")
def vk_login():
    code = request.args.get('code')

    if not code:
        return redirect(url_for('my_contact'))

    response = requests.get(
        "https://oauth.vk.com/access_token?client_id=7858920&client_secret=TDik1LeKLQ73G7opyiaJ&redirect_uri=http://178.154.212.140/vk_login&code=" + code)
    vk_access_json = json.loads(response.text)
    print('get access')
    if "error" in vk_access_json:
        return redirect(url_for('my_contact'))
    print('no error')
    vk_id = vk_access_json['user_id']
    access_token = vk_access_json['access_token']
    print('take access token')
    response = requests.get('https://api.vk.com/method/users.get?user_ids=' + str(
        vk_id) + '&fields=bdate&access_token=' + access_token + '&v=5.130')
    vk_user_json = json.loads(response.text)
    print('get response from api.vk')
    user = Users.query.filter_by(vk_id=vk_id).first()
    if user is None:
        print('no such user')
        name = vk_user_json['response'][0]['first_name'] + \
            " " + vk_user_json['response'][0]['last_name']
        new_user = Users(name=name, vk_id=vk_id, vk_access_token=access_token)
        try:
            db.session.add(new_user)
            db.session.commit()

        except SQLAlchemyError as err:
            db.session.rollback()
            error = str(err.dict['orig'])

            print(f"ERROR adding user to DB: {error}")

            return redirect(url_for('my_contact'))

        user = Users.query.filter_by(vk_id=vk_id).first()

    session['user_id'] = user.id
    return redirect(url_for('my_contact'))
###############################################################################################################################################################
	
if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
