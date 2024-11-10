from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models import *

# @app.route('/login')
# def login():
#     return render_template('login.html')

#services import
def get_service():
    services = Services.query.all()  #it will give a list of all services available, like S1,S2...
    return services

# category import
def get_category():
    categories = Category.query.all()
    return categories

#services by id.
def get_service_by_id(service_id):
    service = Services.query.filter_by(id=service_id).first()   #give 1st ele of list services. in which id matched.
    return service

# services = get_service()[0].name    it will only work if services are there if no services are it will throgh out of range error.
# print(services)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_pass = request.form.get('c_password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        if password == confirm_pass:
            usr = User.query.filter_by(email = email).first()  #password may be same , but user must be diff.
            if usr:
                return render_template('signup.html' , msg='This email id is already registered, try new one')
            new_user = User(email=email , password=password , name= name,address=address,pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html' , msg="Registration Successful , now try login")
        else:
            return render_template('signup.html',msg="Confirm Password didn't match")
            #  give the template showing confirm password is wrong or any other practice.
    return render_template('signup.html')

@app.route('/professional_signup')
def signup1p():
    return render_template('p-signup.html')




#creating login to admin , customer reddirect.
@app.route('/' , methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('email')
        pwd = request.form.get('password')
        usr = User.query.filter_by(email = uname , password = pwd ).first()
        if usr  and usr.role == 0:
            return redirect(url_for('admin_dashboard',user=uname,services=get_service() ))
            # return render_template("admin.html",user=uname,services=get_service())  
              #it will redirect to new route . #router func or jinja var in admin.html
        elif usr and usr.role == 1:
            return render_template('customer.html',user = uname)
        else:
            return render_template('login.html',msg="Invalid Credentials")
    return render_template('login.html')



# ===========================admin related things=====================


# #Common Route for admin , name is the admin email or username.
@app.route('/admin/<user>' , methods=['GET','POST'])
def admin_dashboard(user):
    return render_template('admin.html',user=user,services= get_service())   
    #yaha services explicitly mention krna pada kyu ki upr vala router mein only name hain.


#route for add service
@app.route('/admin/add_service',methods=['GET','POST'])
def add_service():
    usr = User.query.filter_by(role = 0).first()  #it will give admin first record in a list, we have 1 admin only.
    if request.method == 'POST':
        category = request.form.get('category')    #string but in service db we have c_id
        name = request.form.get('name')             #string
        base_price = request.form.get('base_price')   #<class 'NoneType'> ac to type (base_price)  so make it int.
        description = request.form.get('description')  #string
        c_id= Category.query.filter_by(name=category).first() #will give 1st category name.
        #cid.id means id for category name
        available_ser = Services.query.filter_by(name=name).first()  
        #output is already available service witha particular name.
        if available_ser:
            return  render_template('add_service.html',categories=get_category(),user=usr.email,msg='The Service You Want to add already exists.')
            #it will render the page with error message and all template variables.
         
        new_service= Services(c_id=c_id.id,name=name,base_price=base_price,description=description)
        db.session.add(new_service)
        db.session.commit()
        return render_template('admin.html', services = get_service(),user=usr.email,msg='Service Added Successfully')
        
    
    return render_template('add_service.html',categories=get_category(), user=usr.email)


#important learning, pls do check name is defined in html file.
 
 

#routes for edit or delete.
@app.route('/edit_service/<id>/<user>' , methods = ['GET','POST'])
def edit_service(id,user):
    service = get_service_by_id(id)
    if request.method == 'POST':
        category = request.form.get('category')   #string
        print(category)
        name = request.form.get('name')            
        base_price = request.form.get('base_price')
        description = request.form.get('description')
        c_id = Category.query.filter_by(name=category).first()
        #cid.id means id for category name
        service.c_id = c_id.id
        service.name = name
        service.base_price = base_price
        service.description = description
        db.session.commit()
        return redirect(url_for(admin_dashboard(user=user)))
    
    return render_template('edit_service.html',service=service,user=user,categories = get_category())

 
 
@app.route('/delete_service/<id>/<user>' , methods =['GET','POST'])
def delete_service(id,user):
    service = get_service_by_id(id)
    if request.method == 'POST':
         
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for(admin_dashboard(user=user,msg='Service deleted Successfully')))
    return render_template('delete_service.html',service=service,user=user)
#here category render is not req as we are deleting.
    