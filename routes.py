from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models import *
from datetime import datetime
import pytz
from sqlalchemy import func  #important for sum , count use.
import matplotlib   #this is must if we are using plotting , otherwise error flow up.
import matplotlib.pyplot as plt
# matplotlib.use('Agg')  # Use a non-interactive backend


# ============things to learn===========
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace the database URL with your own
engine = create_engine("sqlite:///instance/db.sqlite3")

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session instance
session = Session()

# ===============================================
 

#services import
def get_service():
    services = Services.query.all()  #it will give a list of all services available, like S1,S2...
    return services  #give list

# category import
def get_category():
    categories = Category.query.all()
    return categories  #give list
#professionals import
def get_professional():
    professionals = Professional.query.all()
    return professionals  #give list

#services by id. it is not giving all sevices by cat id , pls be careful.
def get_service_by_id(service_id):
    service = Services.query.filter_by(id=service_id).first()   #give 1st ele of list services. in which id matched.
    return service
def get_all_services_by_cid(id):
    # id is cid in service table
    services = Services.query.filter_by(c_id = id).all()  #will gie list of services belongs to cid.
    return services

#all services by customer  for customer dashboard
def get_all_services_by_customer(customer_id):
    services = Running.query.filter_by(u_id = customer_id).all()  #will give list of obj services u_id is user id.
    #customer is user. 
    return services
#services  in running by sid.
def get_running_pending_services(sid):
    running_services = Running.query.filter_by(s_id = sid,status='pending').all()  #all running services by sid.
    return running_services

#accepted services by professional which are Active or approvved by them
def get_accepted_services_by_professional(professional_id):
    accepted_services = Running.query.filter_by(p_id = professional_id,status='Accepted').all()
    #by problem statement a professional can work on 1 service until customer closes it.
    return accepted_services
#closed services by professional
def get_closed_services_by_professional(professional_id):
    closed_services = Running.query.filter_by(p_id = professional_id,status='closed').all()  #'closed' take care
    return closed_services
 
#functions for search
def search_by_service_name(service_name):
    by_services = Services.query.filter(Services.name.ilike(f"%{service_name}%")).all()
    return by_services  #return a list as .all
def search_by_service_description(service_description):
    by_services_description = Services.query.filter(Services.description.ilike(f"%{service_description}%")).all()
    return by_services_description
def search_by_category(category_name):
    by_category = Category.query.filter(Category.name.ilike(f"%{category_name}%")).all()
    return by_category  #return a list as .all , not useful for us in customer search , as it will return category but we wan to book service i.e not related to anything.

def search_by_category_for_customer(category_name):
    by_category = Category.query.filter(Category.name.ilike(f"%{category_name}%")).first() #limitation , only 1st .
    services = by_category  # return a list of serices related to category
    return services
def search_by_location_for_customer(location):
    by_location = Professional.query.filter(Professional.address.ilike(f"%{location}%")).all() #all professionals which filter location or address , then we iterate in jinja template html. to fethch accurate data.
    return by_location
def search_by_pincode_for_customers(pincode):
    by_pincode = Professional.query.filter(Professional.pincode == pincode).all() 
    #similar to location but pincode is integer so acordingly we queried
    return by_pincode


#search for professional functionality
def search_by_professional_c_name(pid,user_name):
    professionals_running = Running.query.filter(Running.p_id == pid, Running.user.has(User.name.ilike(f"%{user_name}%"))).all()
    services = professionals_running
    return services
def search_by_professional_c_location(pid,user_location):
    professionals_running = Running.query.filter(Running.p_id == pid, Running.user.has(User.address.ilike(f"%{user_location}%"))).all()
    services = professionals_running
    return services   #list
def search_by_professional_c_pincode(pid,pincode):
    professionals_running = Running.query.filter(Running.p_id == pid, Running.user.has(User.pincode == pincode)).all()
    services = professionals_running
    return services

    


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

# @app.route('/professional_signup')
# def signup1p():
#     return render_template('p-signup.html')




#creating login to admin , customer reddirect.
@app.route('/' , methods=['GET','POST'])
def login():
    msg = request.args.get('msg')  
    #getting from parameter passing while redirecting from any other route. 260 line-no.
    if request.method == 'POST':
        uname = request.form.get('email')
        pwd = request.form.get('password')
        usr = User.query.filter_by(email = uname , password = pwd ).first()
        professional = Professional.query.filter_by(email=uname).first()
        #tell professional name
        if usr  and usr.role == 0:
            return redirect(url_for('admin_dashboard',user=uname))
            # return render_template("admin.html",user=uname,services=get_service())  
              #it will redirect to new route . #router func or jinja var in admin.html
        elif usr and usr.role == 1:
            return  redirect(url_for('customer_dashboard',user=uname))
        elif professional and professional.status == 1:
            return redirect(url_for('professional_dashboard',user=professional.email, sid= professional.s_id))
            #professional.name is better in elif if professional is none , we saved by error.
        elif professional and professional.status == 0:
            return render_template('login.html',msg="Your Account is Under Verification")
        elif professional and professional.status == 2:
            return render_template('login.html',msg="You Account is blocked")
        
        else:
            return render_template('login.html',msg="Invalid Credentials")
    return render_template('login.html',msg=msg)



# ===========================admin related things=====================


# #Common Route for admin , name is the admin email or username.
@app.route('/admin/<user>' , methods=['GET','POST'])
def admin_dashboard(user):
    return render_template('admin.html',user=user,services= get_service(),professionals = get_professional())   
    #yaha services explicitly mention krna pada kyu ki upr vala router mein only name hain.

#admin professional
# pid is professional id 
@app.route('/admin/professional/manage/<pid>/<user>/<value>',methods = ['GET','POST'])
# value is Approve or Block kinda constant.
def manage_professional(pid,user,value):
    value = value
    professional = Professional.query.filter_by(id=pid).first()   #the one who the pid belongs .
    if request.method == 'POST' and value == 'Approve':
        professional.status = 1
        db.session.commit()
        return redirect(url_for('admin_dashboard',user = user))
    elif request.method == 'POST' and value == 'Block':
        professional.status = 2
        db.session.commit()
        return redirect(url_for('admin_dashboard',user = user))
    return render_template('warning.html',professional = professional, value=value, pid = pid , user=user)


#user is already passed in admin file.
@app.route('/admin/<user>/show/all_professionals')
def show_all_professionals(user):
    user = user
    professionals = Professional.query.all()
    return render_template('all_professionals.html',professionals = professionals,user=user)

@app.route('/admin/<user>/<pid>/details')
def show_professional_details(user,pid):
    professional = Professional.query.filter_by(id = pid).first()  #professional object related to pid.
    return render_template('particular_professional_details.html',professional = professional,user=user)







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

#add category to admin
@app.route('/admin/add_category',methods=['GET','POST'])
def add_category():
    usr = User.query.filter_by(role = 0).first()  #it will give admin first record in a list, we have 1 admin only.
    if request.method == 'POST':
        name = request.form.get('name')             #string
        category_name = Category.query.filter_by(name = name).first()
        if category_name :
            pass
        else:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for('admin_dashboard', user = usr.email))
    return render_template('add_categories.html',user = usr.email)    
 
 

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

 




# ====================================customer stuff==============================


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
    service = Services.query.filter_by(id = sid).first()  # give 1st obj in list.
    if request.method=='POST':
        already_service_status = Running.query.filter_by(u_id = uid ,status='pending').first()
        already_service_status2 = Running.query.filter_by(u_id = uid , status = 'Accepted').first()
        #it will take care that if pending is there they can't book another.
        if already_service_status:
            return render_template('book_services.html',msg='You already booked one service kindly wait for acceptence',user=user,sid=sid,id=uid)
            #all these sid, user are necessary , as navbar will need or nav bar some router.
        elif already_service_status2:
            return render_template('book_services.html',msg='Kindly close the active service before procedding',id = uid,user = user ,sid = sid )
        cid = Services.query.filter_by(id = sid).first().c_id
        # Set the current time in UTC+5:30 (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')   #indian standard time
        current_time = datetime.now(ist_timezone)
        # Get the current time in IST timezone and remove microseconds
        current_time = datetime.now(ist_timezone).replace(microsecond=0)  
        new_service_rq_added = Running(u_id=uid,s_id=sid,c_id=cid,date_time_created=current_time)
        db.session.add(new_service_rq_added)
        db.session.commit()
        return redirect(url_for('customer_dashboard',user=user))
     
    return render_template('book_services.html',user=user,sid=sid,id=uid,service=service)

#get details of particular customer services
@app.route('/customer/<uid>/<user>/services',methods=['GET','POST'])
def all_customer_services(uid,user):
    services = get_all_services_by_customer(uid)   # running services uid is customer id , cid we call category id , don't confuse.
    return render_template('customer_services.html',services=services,user=user,id=uid)


#it is only rendered if customer on close it , as on other buttons , no close route is defined.
@app.route('/customer/<id>/<user>/services/close',methods = ['GET','POST'])
def close_service(id,user):
    service = Running.query.filter_by(u_id=id,status = 'Accepted').first()  
    #accepted condn is must, only accepted close.
    if request.method == 'POST':
        service.status = 'closed'
        # we can 1st do rating and then service.rating change , do it directly instead
        service.ratings = request.form.get('rating')  #rating is in str in database Running class.
        service.remarks = request.form.get('remarks')
        ist_timezone = pytz.timezone('Asia/Kolkata')   #indian standard time
        current_time = datetime.now(ist_timezone)
        # Get the current time in IST timezone and remove microseconds
        current_time = datetime.now(ist_timezone).replace(microsecond=0)
        service.date_time_closed = current_time
        db.session.commit()
        return redirect(url_for('all_customer_services',uid=id,user=user))
        #all customer service redirect have all necessary equipments.  it need id in form of uid. 
    return render_template('customer_remarks.html',uid = id , user = user,service =service,header= 'Your opinion matters?', action = 'close')    

#revoking service .
# id is uid dont forgot.
@app.route('/customer/<id>/<user>/services/revoke', methods = ['GET','POST'])
def revoke_service(id,user):
    service = Running.query.filter_by(u_id=id,status = 'pending').first()  #only pending can revoke.
    if request.method == 'POST':
        service.status = 'Revoked'
        db.session.commit()
        return redirect(url_for('all_customer_services',uid=id,user=user))
    return render_template('service_revoke.html',user = user , uid = id ,service=service)


#edit a rating or remarks on closed service
@app.route('/customer/<id>/<user>/services/edit_review',methods = ['GET','POST'])
def edit_service_review(id,user):
    service = Running.query.filter_by(u_id=id,status = 'closed').first()  #only closed service extract
    if request.method == 'POST':
        service.ratings = request.form.get('rating')  #rating is in str in database Running
        service.remarks = request.form.get('remarks')
        # closed time have to be same , only rating or remarks can be changed
        db.session.commit()
        return redirect(url_for('all_customer_services',uid=id,user=user))
    return render_template('customer_remarks.html',user=user,uid = id, service = service ,action = 'edit_review' )


#customer search
@app.route('/search/customer/<user>/services/', methods = ['GET','POST'])
def search_services_for_customer(user):
    if request.method == 'POST' :
        uid = User.query.filter_by(email = user).first().id   #uid is required for layout incude .
        search_txt = request.form.get('search_txt')
        by_services = search_by_service_name(search_txt)   #return a list of objects.
        by_services_description = search_by_service_description(search_txt)   #return a list of objects.
        by_categories = search_by_category_for_customer(search_txt)
        by_pincode = search_by_pincode_for_customers(search_txt)
        if by_categories:
            by_categories = by_categories.services 
            #to get rid of none type error  
        #give serices related to category list of obj. in function category.services . look carefully,don't confuse.
        by_address = search_by_location_for_customer(search_txt)    
        if by_services:
            return render_template('search_customer.html',user=user,services = by_services, id = uid,msg='Best results for your search.')
        elif by_services_description:
            return render_template('search_customer.html',user=user,services = by_services_description, id = uid,msg='Best results for your search.')
        elif by_categories:
            return render_template('search_customer.html',user=user, services = by_categories , id = uid,msg='Best results for your search.')
        elif by_address:
            return render_template('search_customer.html',user=user, by_address = by_address ,id = uid,msg='Best results for your search.')
        elif by_pincode:
            return render_template('search_customer.html',user=user, by_pincode = by_pincode ,id = uid,msg='Best results for your search.')
        else :
            return render_template('search_customer.html',user=user, id = uid,msg = 'Nothing Found , Search again!')
    



# ======================================Professional things =============================
#professional signup.
@app.route('/professional_signup' , methods=['GET','POST'])
def professional_signup():
    services = get_service() #return a list of obj of all services.
    if request.method=='POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password').strip()
        confirm_pass = request.form.get('c_password').strip()  #if any extra spaces then clear.
        service_name = request.form.get('service')
        address = request.form.get('address')
        experience = request.form.get('experience')
        description = request.form.get('description')
        pincode = request.form.get('pincode')
        status = 0 #by default until admin approves him.
        if password == confirm_pass:
            print('If qst block rendered')
            professional = Professional.query.filter_by(email = email).first() 
            sid = Services.query.filter_by(name=service_name).first().id  #tells sid for service name .
            #password may be same , but professioanl must be diff.
            cid = Services.query.filter_by(name=service_name).first().c_id #tells cid for service.
            if professional:
                return render_template('p-signup.html' , msg='This email id is already registered, try new one')
            new_professional = Professional(email=email , name= name , password=password ,description=description, category = cid,s_id = sid,address=address, experience= experience,pincode=pincode  , status = status   )
            db.session.add(new_professional)
            db.session.commit()
            return redirect(url_for('login' , msg="Registration Successful ,wait for admin to approve"))
        
    return render_template('p-signup.html',services = services)


#passing requests to dashboard
@app.route('/professional/<sid>/<user>')
def professional_dashboard(user,sid):
    p_id = Professional.query.filter_by(email = user).first().id  
    active_services = get_accepted_services_by_professional(p_id)
    services = get_running_pending_services(sid)
    closed_services = get_closed_services_by_professional(p_id)
    return render_template('professional_dashboard.html',user=user,services = services,sid=sid,p_id = p_id , active_services = active_services,closed_services= closed_services)

#professional profile view only
@app.route('/professional/<sid>/<user>/profile',methods = ['GET','POST'])
def professional_profile(sid,user):
    professional = Professional.query.filter_by(email = user).first()
    if request.method == 'POST':
        professional.name = request.form.get('name')
        professional.description = request.form.get('description')
        professional.address = request.form.get('address')
        professional.pincode = request.form.get('pincode')
        professional.experience = request.form.get('experience')
        db.session.commit()
        return redirect(url_for('professional_dashboard',sid=sid,user=user))
    return render_template('professional_profile.html',user=user,sid=sid,professional = professional)




#accepting service requests.
#rsid is id of running pending service.
@app.route('/professional/<sid>/<user>/accept/<rsid>')
def accept_running_service(sid,user,rsid):
    professional = Professional.query.filter_by(email = user).first()
    service = Running.query.filter_by(id=rsid).first()   #give the running service by rsid .
    service.status = 'Accepted' #accept the service.
    service.p_id = professional.id
    db.session.commit()
    return redirect(url_for('professional_dashboard',user=user,sid=sid))


#searching closed or running services by their location , pincode , customer_name
@app.route('/search/professional/<sid>/<user>',methods=['GET','POST'])
def search_services_for_professional(sid,user):
    if request.method == 'POST':
        pid = Professional.query.filter_by(email = user).first().id
        search_txt = request.form.get('search_txt')
        # gives all services irrespective of status , is a list.
        searched_services_by_location = search_by_professional_c_location(pid,search_txt) #list 
        searched_services_by_pincode = search_by_professional_c_pincode(pid,search_txt)  #list
        searched_services_by_customer_name = search_by_professional_c_name(pid,search_txt) #list
        if searched_services_by_location:
            return render_template('professional_dashboard.html', services_search = searched_services_by_location,user = user,sid = sid)
        elif searched_services_by_pincode:
            # print(type(search_txt))
            return render_template('professional_dashboard.html', services_search = searched_services_by_pincode,user = user,sid = sid)
        elif searched_services_by_customer_name:
            return render_template('professional_dashboard.html', services_search = searched_services_by_customer_name,user = user,sid = sid)
        else:
            return render_template('professional_dashboard.html',user= user,sid = sid)
 
    return render_template('professional_dashboard.html',user=user,sid = sid)


# ==================================Charts Stuff ==================================

#support function for plot
def get_services_summary_admin():
    categories = get_category()  #defined fn give a list of all category objects
    summary = {}  #as plotting need data in key , value pair
    for cat in categories:
        available_service_count_per_cat = len(cat.services)
        summary[cat.name] = available_service_count_per_cat
    x_category = list(summary.keys())
    y_service_count = list(summary.values())
    plt.bar(x_category,y_service_count,color = 'blue',width=0.4)
    plt.title('Category/Services')
    plt.xlabel('Category')
    plt.ylabel('Services')
    return plt


#from running services table
def get_records_customer_summary(uid):
    pending = Running.query.filter_by(u_id = uid,status = 'pending').all()  #it gives always 1 as per our conditions.
    accepted = Running.query.filter_by(u_id = uid, status = 'Accepted').all()  #it is also 1 as till closed no bookings.
    closed = Running.query.filter_by(u_id = uid, status = 'closed').all()
    revoked = Running.query.filter_by(u_id = uid, status = 'Revoked').all()  
    #list we want how many record are there belongs to uid.
    #names look carefully as , Accepted in capital , or closed in small like
    closed_count = len(closed)
    accepted_count = len(accepted)
    revoked_count = len(revoked)
    pending_count = len(pending)
    summary = {}
    list_ele = ['pending','accepted','closed','revoked']
    for l in list_ele:
        if l == 'pending':
            summary[l] = pending_count
        elif l == 'accepted':
            summary[l] = accepted_count
        elif l == 'closed':
            summary[l] = closed_count
        elif l == 'revoked':
            summary[l] = revoked_count
        else:
            pass
    x_status = list(summary.keys())
    y_status_count = list(summary.values())
    plt.bar(x_status,y_status_count,color = 'blue',width=0.4)
    plt.title('Status/Records')
    plt.xlabel('Status')
    plt.ylabel('Records')
    return plt


@app.route('/admin/<user>/summary')
def admin_summary(user):
    plot1 = get_services_summary_admin()
    plot1.savefig('static/images/category_admin_summary.jpeg')
    plot1.close()   #it will close the plot.
    return render_template('admin_summary.html' , user= user)

@app.route('/customer/<uid>/<user>/summary')
def customer_summary(uid,user):
    plot = get_records_customer_summary(uid)
    # in string {var} means var , formatted str concept
    filename = f'static/images/customer_summary_{uid}.jpeg'  # Include uid in the filename
    plot.savefig(filename)
    plot.close()
    # plot.clf() dont use it , it will throgh error of gui user
    return render_template('customer_summary.html', user=user, id=uid)

    
