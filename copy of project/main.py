import sys
from tkinter import NO
from xmlrpc.client import TRANSPORT_ERROR
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask import Flask, send_from_directory, request, render_template, redirect, url_for, session, jsonify, flash
from datetime import datetime

app = Flask(__name__, static_url_path="/static")
app.secret_key = '123dormitory'

# Establishing a database connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "password@1234",  
    "database": "dormitory"
}

DORMITORY_CAPACITY = 6 

# A ROUTE IS BASICALLY THE URL FOR THE PAGE YOUR TRYING TO EXECUTE A FUNCTION FOR
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
      if 'username' in session:
        return render_template('dashboard.html')

      else:
          return "An Error occured while loading your dashboard"


@app.route('/anotherlogin', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['username'] = user['username']
                flash('Login successful!')
                return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page
            else:
                flash('Invalid Username or password')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('anotherlogin.html')

@app.route('/dormitories')
def dormitories():


    return render_template('dormitories.html')

@app.route('/add_admin')
def get_admin():
    return render_template('registration.html')

@app.route('/resetpassword')
def forget_pass():
    return render_template('resetpass.html')



@app.route('/reset_password', methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check if the email exists
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Email exists, update the password
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                cursor.execute("UPDATE admin SET password = %s WHERE email = %s", (hashed_password, email))
                conn.commit()
                flash('Password reset successfully!')
            else:
                # Email does not exist
                flash('Email not found!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('reset_password'))
    
    return render_template('reset_password.html')

@app.route('/registration', methods=["POST", "GET"])
def add_admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor = None  
        conn = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("INSERT INTO admin(username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            flash('Admin added successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            if cursor is not None:  
                cursor.close()
            if conn is not None:
                conn.close()
        
        return redirect(url_for('add_admin'))
    
    return render_template('registration.html')



#THIS ROUTE IS FOR DISPLAYING THE MEMBERS, SPECIFICALLY CREATED FOR THE DISPLAY.HTML 
@app.route('/display_members') 
def get_members ():
    try:
        conn = mysql.connector.connect(**db_config) #HERE WE'RE ESTABLISHING CONNECTION TO THE DATABASE SO THAT WE CAN WORK WITH SQL STATEMENTS
        cursor =conn.cursor(dictionary = True)

        cursor.execute("""
                       select dm.Admission_NO, 
                       dm.Fisrt_Name,
                       dm.Last_Name,
                       dm.Class, 
                       dm.dormitory_id,
                       d.dormitory_name,
                       dm.amount_paid, (40000 - dm.amount_paid) as balance
                       FROM
                        dormitory_members dm
                       JOIN
                       dorms d ON dm.dormitory_id = d.dormitory_id
                       """)
        members = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template('display.html', members=members) ###THIS IS WHAT THE FUNCTION SHOULD RETURN IF THE CONNECTION IS SUCCESSFUL. IT WILL GET THE DISPLAY.HTML
                        #THEN THE MEMBERS WILL BE STORED IN THE VARIABLE MEMBERS

    except mysql.connector.Error as err:
        print(f"Error: {err}") #THIS IS HANDLING ERRORS INCASE THE TRY STATEMENT FAILS
        return None
    
@app.route ('/add_new', methods=['GET', 'POST']) #SO NOW WE'RE DONE WITH DISPLAYING THE AVAILABLE DORMITORY MEMBERS AND NOW WE ARE  GOING TO ADD NEW MEMBERS TO THE DATABASE
def New (): #REMEMBER THE FLASK ROUTE SHOULD ALWAYS BE FOLLOWED BY A FUNCTION. THIS IS A FUNCTION THAT CHECKS WHETHER THE FORM CREATED IN THE ADDNEWMEMBERS IS "POSTING" OR "GETTING" INFO FROM THE DATABASE. IN THIS INSTANCE, 
    #SINCE WE'RE POSTING(ADDING) MEMBERS TO THE DATABASE, THE METHOD IS POST. SO WE HAVE THIS IF STATEMENT. 
    if request.method =='POST':
        F_name = request.form["fname"] #THESE ARE JUST VARIABLES THAT WE SHALL USE LATER IN ANOTHER FUNCTION FOR ACTUALLY COMMITTIING THE CHANGES TO THE DATABASE
        L_name = request.form ["lname"] #WHAT'S HAPPENIING HERE IS THAT WE ARE DECLARING A VARIABLE, THEN RETRIEVING THE DATA ENTERED BY THE USER. FOR EXAMPLE IN THIS CASE WE HAVE L_name, which retrieves the last name entered ny the user. as you can see it is requesting for data in the form for the input field with that name lname
        class_name = request.form["class_name"]
        Adm = request.form["Adm"]
        dormitory_id = request.form['dormitory']
        cubicle_id = request.form['cubicle']
        bed_id = request.form['bed']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor (dictionary = True)

            cursor.execute(
                "INSERT INTO dormitory_members (Fisrt_Name, Last_Name, Class, Admission_NO, dormitory_id, cubicle_id, bed_number) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (F_name, L_name, class_name, Adm, dormitory_id, cubicle_id, bed_id)
            )            
            cursor.execute('UPDATE beds SET is_occupied = TRUE WHERE bed_id =%s',(bed_id,) )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect( url_for('dashboard'))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor (dictionary = True)

        cursor.execute('SELECT * FROM dorms')
        dormitories = cursor.fetchall()

        cursor. execute('SELECT * FROM cubicles')
        cubicles =cursor.fetchall()

        cursor.execute('SELECT * FROM beds WHERE is_occupied = FALSE')
        beds= cursor.fetchall()
        
        cursor.close()
        conn.close

        return render_template('addnewmembers.html',dormitories=dormitories, cubicles=cubicles, beds=beds)
    return render_template('display.html')

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/get_cubicles/<int:dormitory_id>', methods=['GET'])
def get_cubicles(dormitory_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch cubicles for the selected dormitory
    cursor.execute("SELECT * FROM cubicles WHERE dormitory_id = %s", (dormitory_id,))
    cubicles = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify({'cubicles':cubicles})   
@app.route('/get_beds/<int:cubicle_id>', methods=['GET'])
def get_beds(cubicle_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch cubicles for the selected dormitory
    cursor.execute("SELECT * FROM beds  WHERE cubicle_id = %s and is_occupied=FALSE" , (cubicle_id,))
    beds = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify({'beds':beds}) 
#the function below is essential for getting the user id so that we can use it in the later functions to delete or modify

def get_user_details(adm):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dormitory_members WHERE Admission_NO = %s", (adm,))

        user_details=cursor.fetchone()
        cursor.close()
        conn.close()
        return user_details
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


@app.route('/del_user', methods = ['GET', 'POST']) #This route is just for deleting users in the display page
def del_user():
    if request.method == 'POST':
        adm = request.form['adm_delete']
        if delete(adm):
            return redirect(url_for('get_members'))
        else:
            return "Error deleting user"
    return render_template('delete.html')
def get_adm(adm):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dormitory_members WHERE Admission_NO = %s", (adm,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None



def delete(adm):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor=conn.cursor()
        cursor.execute("DELETE FROM dormitory_members WHERE Admission_NO =%s", (adm,))
        conn.commit()
        cursor.close()
        conn.close()

        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    
@app.route('/update_user', methods=["POST", "GET"])
def updates():
    if request.method == "POST":
        Adm = request.form['adm_update']
        user = get_adm(Adm)

        if user:
            return redirect(url_for('update_user_details', user_id=user['Admission_NO']))
        else:
            return "No Student with that ID"
    
    return render_template('update.html')


    
@app.route('/update_user_details/<int:user_id>', methods=['GET', 'POST'])
def update_user_details(user_id):
    if request.method == 'POST':
        F_name = request.form["fname"]
        L_name = request.form["lname"]
        class_name = request.form["class_name"]
        dormitory_id = request.form['dormitory']
        cubicle_id = request.form['cubicle']
        bed_id = request.form['bed']
        amount_paid = request.form['amount_paid']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Update existing member
            cursor.execute(
                "UPDATE dormitory_members SET Fisrt_Name=%s, Last_Name=%s, Class=%s, dormitory_id=%s, cubicle_id=%s, amount_paid=%s, bed_number=(SELECT bed_number FROM beds WHERE bed_id=%s) WHERE Admission_NO=%s",
                (F_name, L_name, class_name, dormitory_id, cubicle_id,amount_paid, bed_id, user_id)
            )
            cursor.execute('UPDATE beds SET is_occupied = TRUE WHERE bed_id = %s', (bed_id,))

            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    else:
        user = get_adm(user_id)
        if not user:
            return "User not found", 404

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM dorms')
        dormitories = cursor.fetchall()

        cursor.execute('SELECT * FROM cubicles')
        cubicles = cursor.fetchall()

        cursor.execute('SELECT * FROM beds WHERE is_occupied = FALSE')
        beds = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('update.html', user=user, dormitories=dormitories, cubicles=cubicles, beds=beds)



@app.route('/dormitory_status')
def dormitory_status():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT
        d.dormitory_name,
        d.total_cubicle,
        d.total_beds_per_cubicle,
        (d.total_cubicle * d.total_beds_per_cubicle) AS total_beds,
        COUNT(b.bed_id) AS occupied_beds,
        ((d.total_cubicle * d.total_beds_per_cubicle) - COUNT(b.bed_id)) AS available_beds
    FROM
        dorms d
    LEFT JOIN
        cubicles c ON d.dormitory_id = c.dormitory_id
    LEFT JOIN
        beds b ON c.cubicle_id = b.cubicle_id AND b.is_occupied = TRUE
    GROUP BY
        d.dormitory_name, d.total_cubicle, d.total_beds_per_cubicle
    ORDER BY
        d.dormitory_name;
    """
    
    cursor.execute(query)
    status_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('dormitories.html', status_data=status_data)

if __name__ == '__main__':
    app.run(debug=True)
    
