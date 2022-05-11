from flask import Flask,render_template,request,flash,redirect,url_for
import os
import sqlite3
import pandas as pd

from flask import Flask, url_for, render_template, flash, request, redirect, session,logging,request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['UPLOAD_FOLDER']="C:/project4/static/Excel"
app.secret_key="123"

con=sqlite3.connect("MyData.db")
con.execute("create table if not exists data(pid integer primary key,exceldata TEXT)")
con.close()


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	phone = db.Column(db.String(80))
	email = db.Column(db.String(80))
	password = db.Column(db.String(80))

	def __init__(self, username, password):
		self.username = username
		
		self.password = password
db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		try:
			data = User.query.filter_by(username=name, password=passw).first()
			if data is not None:
				session['logged_in'] = True
				return redirect(url_for('index'))
			else:
				return 'Incorrect Login'
		except:
			return "Incorrect Login"

@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')
	



@app.route("/transactions",methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:


        con = sqlite3.connect("MyData.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from data")
        data = cur.fetchall()
        con.close()

        if request.method == 'POST':

            uploadExcel = request.files['uploadExcel']

            if uploadExcel.filename != '':

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploadExcel.filename)
                uploadExcel.save(filepath)
                con = sqlite3.connect("MyData.db")
                cur = con.cursor()
                cur.execute("insert into data(exceldata)values(?)", (uploadExcel.filename,))
                con.commit()
                flash("Excel Sheet Upload Successfully", "success")


                con = sqlite3.connect("MyData.db")
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute("select * from data")
                data = cur.fetchall()
                con.close()
            return render_template("dashboard.html", data=data)

    return render_template("dashboard.html",data=data)

@app.route('/view_excel/<string:id>')
def view_excel(id):
    con = sqlite3.connect("MyData.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from data where pid=?",(id))
    data = cur.fetchall()
    print(data)
    for val in data:
        path = os.path.join("static/Excel/",val[1])
        print(val[1])
        data=pd.read_csv(path)
    con.close()
    return render_template("view_excel.html",data=data.to_html(index=False,classes="table table-bordered").replace('<th>','<th style="text-align:center">'))

@app.route('/delete_record/<string:id>')
def delete_record(id):
    try:
        con=sqlite3.connect("MyData.db")
        cur=con.cursor()
        cur.execute("delete from data where pid=?",[id])
        con.commit()
        flash("Record Deleted Successfully","success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("index"))
        con.close()

if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()