from flask import Flask, render_template, request, session, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from re import search
import math
from datetime import datetime
import os


app = Flask(__name__)
import sqlite3
#better encryption than using a secret key called "secret key"
app.secret_key=str(os.urandom(16))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DailyUpdates.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)  # INITIALIZE THE DATABASE 

class DailyUpdates(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    Name=db.Column(db.String(20),nullable=True)
    Department=db.Column(db.String(40),nullable=True)
    Description=db.Column(db.String(400),nullable=True)
    DT = db.Column(db.String(12), nullable=True)
    
@app.route("/")
def index():
    conn = sqlite3.connect('DailyUpdates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM daily_updates")
    data = c.fetchall()
    return render_template('index.html',data=data)
    








@app.route("/delete/<int:sno>", methods=['GET', 'POST'])
def delete(sno):
    # Only Loggged In user can edit the post
    if ('Admin' in session and session['Admin'] == "ClubIndigo"):
        sno = str(sno)
        post = DailyUpdates.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

# Logout section handles logging out
@app.route("/logout")
def Logout():
    session.pop('Admin')
    return redirect('/dashboard')

# edit section handles editing/creating articles
# <int:sno> forces the get value to only be an integer, saving from XSS
@app.route("/dashboard/edit/<int:sno>", methods=['GET', 'POST'])
def edit(sno):
    # Only Loggged In user can edit the post
    if ('Admin' in session and session['Admin'] == "ClubIndigo"):
        # Checks if form is submitted
        if request.method == 'POST':
            # Vars hold intermediate values that are filled into the form
            
            Name = request.form.get('Title')
            Description = request.form.get('Content')
            Department = request.form.get('WrittenBy')
            now =  datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            Dt = formatted_date



            if sno==0:
                # Post = DailyUpdates(PostTitle=PrevTitle, PostContent=PrevContent, ImgFile=PrevImg, PostedBy=Author, slug=PrevSlug, DT=Dt)
                update = DailyUpdates(Name=Name, Department=Department, Description=Description, DT=Dt)
                db.session.add(update)
                db.session.commit()
                #If the post already exists in the database
            else:
                Post=DailyUpdates.query.filter_by(sno=sno).first()
                Post.Name  = Name
                Post.Department= Department
                Post.Description   = Description
                Post.DT         = Dt
                
                db.session.commit()
                flash("You have edited a Article,successfully ","success")
    
                return redirect('/dashboard/edit/'+str(sno))
    else:
        return redirect('/')        
    Post=DailyUpdates.query.filter_by(sno=sno).first()
    return render_template('edit.html',  Post=Post, sno=sno)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
 # checks if user already logged in
    if ('Admin' in session and session['Admin'] == "ClubIndigo"):
        Post = DailyUpdates.query.all()
        return render_template('adminpanel.html', Posts=Post)
    # Checks if login form submitted
    if (request.method == 'POST'):
        UserName = request.form.get('UserName')
        Password = request.form.get('Password')
        checkuse = "ClubIndigo"
        checkpass = "ClubIndigo"
        if(UserName == checkuse and Password == checkpass):
            # Set The Session Variable
            session['Admin'] = UserName
            Post = DailyUpdates.query.all()

            return render_template('adminpanel.html', Posts=Post)
        else:
            # flash("Your UserName and Password didn't match","danger")
            return render_template('signup.html')
    #    Ridirect To Admin Panel
    else:
        return render_template('signup.html')

if __name__=="__main__":
    app.run(debug=True)