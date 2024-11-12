from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models import *
from datetime import datetime
import pytz


# @app.route('/login')
# def login():
#     return render_template('login.html')

#services import
def get_service():
    services = Services.query.all()  #it will give a list of all services available, like S1,S2...
    return services  #give list

# category import
def get_category():
    categories = Category.query.all()
    return categories  #give list

#services by id. it is not giving all sevices by cat id , pls be careful.
def get_service_by_id(service_id):
    service = Services.query.filter_by(id=service_id).first()   #give 1st ele of list services. in which id matched.
    return service
def get_all_services_by_cid(id):
    # id is cid in service table
    services = Services.query.filter_by(c_id = id).all()  #will gie list of services belongs to cid.
    return services

#functions for search
def search_by_service_name(service_name):
    by_services = Services.query.filter(Services.name.ilike(f"%{service_name}%")).all()
    return by_services  #return a list as .all
def search_by_service_description(service_description):
    by_services_description = Services.query.filter(Services.description.ilike(f"%{service_description}%")).all()
    return by_services_description
def search_by_category(category_name):
    by_category = Category.query.filter(Category.name.ilike(f"%{category_name}%")).all()
    return by_category  #return a list as .all


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
            return redirect(url_for('admin_dashboard',user=uname))
            # return render_template("admin.html",user=uname,services=get_service())  
              #it will redirect to new route . #router func or jinja var in admin.html
        elif usr and usr.role == 1:
            return  redirect(url_for('customer_dashboard',user=uname))
        else:
            return render_template('login.html',msg="Invalid Credentials")
    return render_template('login.html')



# ===========================admin related things=====================


# #Common Route for admin , name is the admin email or username.
@app.route('/admin/<user>' , methods=['GET','POST'])
def admin_dashboard(user):
    return render_template('admin.html',user=user,services= get_service())   
    #yaha services explicitly mention krna pada kyu ki upr vala router mein only name hain.

@app.route('/customer/<user>' , methods=['GET','POST'])
def customer_dashboard(user):
    user_id = User.query.filter_by(email=user).first().id    #tells id for a customer as required in jinja.
    categories= get_category()
    # print('Customer Dashboard',categories[1].name,categories[2].name )
    return render_template('customer.html' ,user=user,categories=categories,id= user_id, header_msg='Looking For?' )

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
        
        name = request.form.get('name')            
        base_price = request.form.get('base_price')
        description = request.form.get('description')
        c_id = Category.query.filter_by(name=category).first()
        #cid.id means id for category name
        if c_id:
            service.c_id = c_id.id
            service.name = name
            service.base_price = base_price
            service.description = description
            db.session.commit()
            return redirect(url_for('admin_dashboard',user=user))
    
        return render_template('edit_service.html',service=service,user=user,categories=get_category(),msg='Category Not Found')
    
    return render_template('edit_service.html',service=service,user=user,categories = get_category())

 
 
@app.route('/delete_service/<id>/<user>' , methods =['GET','POST'])
def delete_service(id,user):
    service = get_service_by_id(id)
    if request.method == 'POST':
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('admin_dashboard',user=user))
    return render_template('delete_service.html',service=service,user=user)
#here category render is not req as we are deleting.
    

    #search fuctionality on services on admin dashboard.
@app.route('/search/<user>' , methods = ['GET','POST'])
def search(user):
    if request.method == 'POST':
        # print("POST request received")
        search_txt = request.form.get('search_txt')
        by_services = search_by_service_name(search_txt)   #return a list of objects.
        by_services_description = search_by_service_description(search_txt)   #return a list of objects.
        if by_services:
            return render_template('admin.html',user=user,services = by_services)
        elif by_services_description:
            return render_template('admin.html',user=user,services = by_services_description)
        else:
            return render_template('admin.html',user=user, msg='No Service Found')
        
    # print("GET request received")    
    return redirect(url_for('admin_dashboard',user = user))


#if role=1 , username is given when login , but we need user id in customer table.
# <category> is a category.name
# we need services related to a particular category
@app.route('/<category>/services/<id>/<user>')
# here id is not cid , here id is uid.
def customer_view(category,id,user):
    cid = Category.query.filter_by(name=category).first().id   #we only have one record of unique category , so first. if all then messy.
    services = get_all_services_by_cid(cid)   #list of all services related to cid or id.
    return render_template('customer.html',services=services,user=user,id=id,category=category,header_msg='Book the service you would like to have !')
#important lesson , jitne attribute def func mein hoo , utne saare use hone chaye , other vise error.

     
@app.route('/book/<user>/<uid>/service/<sid>',methods=['GET','POST'])
def book_service(user,sid,uid):
    if request.method=='POST':
        cid = Category.query.filter_by(id = sid).first().id
        # Set the current time in UTC+5:30 (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')   #indian standard time
        current_time = datetime.now(ist_timezone)
        new_service_rq_added = Running(u_id=uid,s_id=sid,c_id=cid,date_time_created=current_time)
        db.session.add(new_service_rq_added)
        db.session.commit()
        return redirect(url_for('customer_dashboard',user=user))
    service = Services.query.filter_by(id = sid).first()  # give 1st obj in list.
    return render_template('book_services.html',user=user,sid=sid,id=uid,service=service)