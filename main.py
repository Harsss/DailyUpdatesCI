from flask import Flask, render_template, request, session, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from re import search
import math
from datetime import datetime
import os
# # from werkzeug import secure_filename 
# from werkzeug.utils import secure_filename 
# from werkzeug.exceptions import RequestEntityTooLarge 
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
    
# @app.route("/Post/<string:post_slug>", methods=['GET'])
# def post_route(post_slug):
#      # checks that the post slug contains no characters other than alphanumeric ones and '-'
#     # \W = any character not [A-Za-z0-9_]
#     match = search(r"\W", post_slug)
#     # if an unknown character found, redirect to homepage, else render post template with slug as Post.Slug
#     if match:
#         return redirect('/')
#     else:
#         Post = Posts.query.filter_by(slug=post_slug).first()
#         # splits up the content by para so that it's easier to output in the template file. Then resets Post.PostContent to the generated list of paras
#         contenttobreak = Post.PostContent.split('\n')
#         Post.PostContent = contenttobreak
#         return render_template('post.html', Post=Post)












@app.route("/delete/<int:sno>", methods=['GET', 'POST'])
def delete(sno):
    # Only Loggged In user can edit the post
    if ('Admin' in session and session['Admin'] == "IndigoGlobal"):
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
    if ('Admin' in session and session['Admin'] == "IndigoGlobal"):
        # Checks if form is submitted
        if request.method == 'POST':
            # Vars hold intermediate values that are filled into the form
            
            Name = request.form.get('Title')
            Description = request.form.get('Content')
            Department = request.form.get('WrittenBy')
            now =  datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            Dt = formatted_date
            # PrevSlug = request.form.get('Slug')
            # PrevImg = request.form.get('ImageFile')

            # section checks if the slug entered is a repeat value
            # **IDEA: Generate the slug instead of asking the user to enter**
            # Loop goes through each post in the Posts table
            # for post in DailyUpdates.query.all():
                # Need to check if the new slug (PrevSlug) as a slug in a post that isn't the post being edited.
                # using sno as the verifier since sno is the Primary Key of the table
                # LOGIC:
                # Post Ids match    and slugs match     > No Action
                # Post Ids X match  and slugs match     > Error
                # Post Ids match    and slugs X match   > No Action
                # Post Ids X match  and slugs X match   > No Action
                # pass
                # if post.sno != sno and PrevSlug == post.slug:
                #     # flash method passes the error to the redirected page
                #     flash("Another post exists with the same slug, please modify")
                #     return redirect('/dashboard/edit/'+str(sno))
            # for creating a new post, basically uses the same page
            # same pattern matching as in post URL, checking to make sure no special characters are allowed in the slug
            # match = search(r"\W", PrevSlug)
            # if character found, then flash error message
            # if match:
            #     flash(
            #         "Cannot use any character other than A-Z, a-z, 0-9 and _ in the slug")
                # return redirect('/dashboard/edit/'+str(sno))
            # creates a new post, using the same edit page
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
                # Post.ImgFile    = PrevImg
                # Post.slug       = PrevSlug
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
    if ('Admin' in session and session['Admin'] == "IndigoGlobal"):
        Post = DailyUpdates.query.all()
        return render_template('adminPanel.html', Posts=Post)
    # Checks if login form submitted
    if (request.method == 'POST'):
        UserName = request.form.get('UserName')
        Password = request.form.get('Password')
        checkuse = "IndigoGlobal"
        checkpass = "IndigoGlobal"
        if(UserName == checkuse and Password == checkpass):
            # Set The Session Variable
            session['Admin'] = UserName
            Post = DailyUpdates.query.all()

            return render_template('adminPanel.html', Posts=Post)
        else:
            # flash("Your UserName and Password didn't match","danger")
            return render_template('signUp.html')
    #    Ridirect To Admin Panel
    else:
        return render_template('signUp.html')

if __name__=="__main__":
    app.run(debug=True)