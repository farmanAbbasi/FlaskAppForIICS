# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash,g
from functools import wraps
import sqlite3
from passlib.hash import sha256_crypt,pbkdf2_sha256#for password hashing 

#for iics 1--------------------------------------------------------------------------------------------------
import requests
import json
import zipfile
import io
import os,stat
import shutil
import csv,re
import xlrd
from pathlib import Path
path=''
typeOfPath=''
flag=-1
rfc=0
def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
         os.rmdir(os.path.join(root, name))

def putjson(filename,data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def getjson(filepath):
    with open((filepath),'r') as fp:
        return json.load(fp)
#-----------end of 1-----------------------------------------------------------------------------------------      


# create the application object
app = Flask(__name__,static_url_path='/static')

# config
app.secret_key = 'my precious'
app.database = 'sample.db'
app.database2='usersDB.db'

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.','danger')
            return redirect(url_for('login'))
    return wrap


# logout required decorator
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            session.pop('logged_in', None)#logging out
            return render_template('signup.html')
    return wrap



# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    g.db = connect_db()# fun created by us
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0], details=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('index.html', posts=posts)  # render a template
    #return render_template('index.html')  # render a template
    #return "Hello, World!"  # return a string

'''
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template
'''    

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usernameEntered=request.form['username']
        passwordEntered=request.form['password']
        g.db2 = connect_db2()
        hashedPassword = g.db2.execute("SELECT * FROM users WHERE username =:who",{"who":usernameEntered})
        if hashedPassword.fetchone() is not None:
            hashedPassword = g.db2.execute("SELECT password FROM users WHERE username =:who",{"who":usernameEntered})
            hashedPasswordValue=hashedPassword.fetchone()[0]
            if not sha256_crypt.verify(passwordEntered, hashedPasswordValue):
                error = 'Invalid Credentials. Please try again.'
            else:
                session['logged_in']= True
                flash('You were logged in.','success')
                return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.','success')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
@logout_required
def signup():
    error = None
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        password2=request.form['password2']
        email=request.form['email']
        g.db2 = connect_db2()
        uname = g.db2.execute("SELECT username FROM users WHERE username =:who",{"who":username})
        eml=g.db2.execute("SELECT email FROM users WHERE email =:whatMail",{"whatMail":email})
        if len(username)<4:
            error = 'Username must be atleast 4 characters long'
        elif uname.fetchone() is not None:
            error = 'Username already exists'
        elif eml.fetchone() is not None:
            error = 'Email already exists'   
        elif  len(password)<4:   
             error = 'Password must be atleast 4 characters long' 
        elif len(email)<3:
            error = 'Invalid email' 

        else:
            if password != password2:
                error = 'Password don\'t match.'
            else:
                flash('Sign up completed','success')
                ## sending to usersDB
                #g.db2 = connect_db2()# function created by us also it is shifted to above as we need to check for existence
                password = sha256_crypt.encrypt(password)#hashing password for security
                print(password)
                g.db2.execute('insert into users (username,password,email) values '\
                    '(?,?,?)',[username,
                                password,
                                email])
                g.db2.commit()
                g.db2.close()
                #fetching the usersDB
                # cur2 = g.db2.execute('select * from users')
                # users = [dict(username=row[0], password=row[1],email=row[2]) for row in cur2.fetchall()]
                # print(users)
                # g.db2.close()
                return redirect(url_for('login'))
    return render_template('signup.html',error=error)  


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    error = None
    rfc=request.form['rfc']
    checkbox=request.form.get('fancycheckboxdefault')
    print(rfc)

    if request.method == 'POST' and len(rfc)>0:
        counter=0
        #_______________________previous login_________________________________
       
        #------------------------------------------end 2------------------------------------------------
        flag=-1
        loc = ("IICS DATA/rfcFile.xlsx")
        # To open Workbook 
        wb = xlrd.open_workbook(loc) 
        sheet = wb.sheet_by_index(0)
        # For number of rows and columns
        rows=sheet.nrows
        columns=sheet.ncols

        
        for i in range(1,rows):
            idsArray2=[]
            if str(int(sheet.cell_value(i,0)))==rfc:
                counter+=1
                dicter={}
                path=sheet.cell_value(i,1)
                typeOfPath=sheet.cell_value(i,2)
                dicter['path']=path
                dicter['type']=typeOfPath
                idsArray2.append(dicter)
                flag=1
                print(idsArray2)

                #if existing go to the import env. and copy on github and then continue as normal 
                if checkbox is not None:
                #ticked
                #connect to import env and copy a version on github
                    print('ticked')
                    

                
                #login#################start###########################
                values = {"username":"mohammadfarmanabbasi2019@gmail.com","password":"Qwerty@123"}
                headers={'content-type':'application/json','accept':'application/json'}
                url1='https://dm-ap.informaticacloud.com/saas/public/core/v3/login'
                r = requests.post(url1,data=json.dumps(values),headers=headers)
                print(r.status_code)

                #convert r into json format
                data = r.json()
                #formatting d json in beautified form
                d=json.dumps(data,indent=2)
                print(d)

                #putting in *.json file
                putjson('IICS DATA/1)loginData.json',data)
                #retrieving data from that file
                myobj=getjson('./IICS DATA/1)loginData.json')

                ics=myobj['userInfo']['sessionId']#NOTE WE ARE SENDING AND THEN RECEIVING THEN PRINTING WE CAN DIRECTLY PRINT ALSO
                #as ics=data['userInfo']['sessionId']
                print(ics)
                #######################################################


            
                #lookup----------------------------------------------------------------------------------------------------------------------------------
                values={
                        "objects": idsArray2 }

                headers={'content-type':'application/json','INFA-SESSION-ID':ics}
                r=requests.post('https://apse1.dm-ap.informaticacloud.com/saas/public/core/v3/lookup',data=json.dumps(values),headers=headers)
                print(r.status_code)

                if r.status_code != 200:
                    print('nothing found')
                else:    
                    data=r.json()
                    d=json.dumps(data,indent=2)
                    print(d)

                    #putting in *.json file
                    putjson('IICS DATA/2)lookup.json',data)
                    #retrieving data from that file
                    myobj=getjson('./IICS DATA/2)lookup.json')


                    #export of all ids-------------------------------------------------------------------------------------------------------------------------------------
                    #getting all the ids of objects dynamically
                    numberOfObjects=len(myobj['objects'])
                    #just for printing ids if will reomove then also no problem

                        
                    idsArray=[]
                    ids=[]
                    for i in range(numberOfObjects):
                        dicter2={}
                        value=myobj['objects'][i]['id']
                        ids.append(value)
                        dicter2['id']=value
                        idsArray.append(dicter2)
                    print(idsArray)
                        
                    #putting ids in a csv file
                    with open('IICS DATA/idsArray.csv', 'w+',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['id'])
                        for val in ids:
                            writer.writerow([val])


                    #idsArray is storing a dict od key : value pairs of id : ids
                    values={
                        "objects": idsArray
                        }
                    headers={'content-type':'application/json','accept':'application/json','INFA-SESSION-ID':ics}
                    r=requests.post('https://apse1.dm-ap.informaticacloud.com/saas/public/core/v3/export',data=json.dumps(values),headers=headers)
                    print(r.status_code)

                    data= r.json()
                    #putting in *.json file
                    putjson('IICS DATA/3)export.json',data)
                    #retrieving data from that file
                    myobj=getjson('./IICS DATA/3)export.json')
                    print(json.dumps(myobj,indent=2))
                    exportId=myobj["id"]
                    print(exportId)

                    #get status of export with id (note: its exported id)---------------------------------------------------------------------------------------------------------
                    headers={'content-type':'application/json','accept':'application/json','INFA-SESSION-ID':ics}
                    r=requests.get('https://apse1.dm-ap.informaticacloud.com/saas/public/core/v3/export/'+exportId,headers=headers)
                    print(r.status_code)
                    data=r.json()
                    putjson('IICS DATA/4)export_status.json',data)
                    myobj=getjson('./IICS DATA/4)export_status.json')
                    print(json.dumps(myobj,indent=2))

                    #download export package----------------------------------------------------------------------------------------------------------------------------------
                    r=requests.get('https://apse1.dm-ap.informaticacloud.com/saas/public/core/v3/export/'+exportId+'/package',headers=headers)
                    print(r.status_code)

                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    if os.path.isdir('export_file'):
                        shutil.rmtree('export_file')#delete the previous folder
                    z.extractall('export_file')

                    #make zip
                    zipOutputName = "export_file_zip"+str(counter)
                    zipName=zipOutputName
                    path = "./export_file"
                    #directory='C:/Users/moabbasi/Desktop/testing'
                    #or
                    #directory inside that folder where .py exists
                    d=os.getcwd()
                    d2=d.split('\\')
                    d3=('/').join(d2)
                    directory=d3+'/gitVersions2approach'
                    if not os.path.isdir(directory):
                        os.makedirs(directory)
                    shutil.make_archive(zipName,'zip',path)
                    #move zip to git wala folder
                    if counter==1:#clear the directory only once
                        pattern="export_file_zip"
                        for f in os.listdir(directory):
                            if re.search(pattern, f):
                                fullpath = os.path.join(directory,f)
                                os.remove(fullpath)
                            
                    if os.path.isfile(directory+'/'+zipOutputName+'.zip'):
                        
                        '''
                        os.rename(zipOutputName+'1.zip', zipOutputName+'2.zip')
                        if os.path.isfile(directory+'/'+zipOutputName+'2.zip'):
                            #delete 1 one rename 2 one and then move here as 2
                            fullpath = os.path.join(directory+'/',zipOutputName+'1.zip')
                            os.remove(fullpath)
                            os.rename(directory+'/'+zipOutputName+'2.zip',directory+'/'+zipOutputName+'1.zip')
                            shutil.move(zipOutputName+'2'+'.zip',directory)
                        else:    
                            shutil.move(zipOutputName+'2'+'.zip',directory)
                            '''

                    else:    
                        shutil.move(zipOutputName+'.zip',directory)

                #logout-----------------------------------------------------------------------------------------------------------------------------------------------
                headers={'content-type':'application/json','INFA-SESSION-ID':ics}
                r=requests.post('https://dm-ap.informaticacloud.com/saas/public/core/v3/logout',headers)
                print(r.status_code)       
            else:
                print('rfc not found')# on each iteration
        if flag==-1:
            flash('RFC not found','danger')  
        else:
            flash('Export Done...','success') 
                
        #--------previous logout--------------------
        
        
        #clearing the from data
        request.form.rfc=''
        rfc=''
        return render_template('index.html')
    else:
        return render_template('index.html')




# connect to database
def connect_db():
    return sqlite3.connect(app.database)

# connect to database2
def connect_db2():
    return sqlite3.connect(app.database2) 
  

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)