from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True , nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    pincode = db.Column(db.Integer , nullable=False)
    role = db.Column(db.Boolean, nullable=False, default=1)
    flag = db.Column(db.Integer,nullable = True, default = 0)  #count the number of flag points
    status = db.Column(db.Integer , nullable=False, default = 1)  #to block status =2 , status =1 normal
    running = db.relationship("Running", backref = 'user',cascade = "all,delete",lazy = True)

  # consider username as email  
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  
    services = db.relationship("Services", backref = 'category',cascade = "all,delete" ,lazy = True)
    running = db.relationship("Running", backref = 'category',cascade = "all,delete",lazy = True)


class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True,nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256),db.ForeignKey('category.id'), nullable=False )  #category is cid consider 
    s_id = db.Column(db.String(256),db.ForeignKey('services.id'), nullable=False )
         #see category in numbers also if possible
    # service = db.Column(db.String(256), nullable=False)
    # pdf = db.Column(db.LargeBinary, nullable=False)
    address = db.Column(db.String(64), nullable=False)
    experience = db.Column(db.String(64), nullable=False)
    pincode = db.Column(db.Integer , nullable=False)
    rating = db.Column(db.String(10), default = 'New Professional')
    status = db.Column(db.Integer , nullable=False)
    #status code 0 when applied , 1 when accepted , 2 when blocked .
    running = db.relationship("Running", backref = 'professional',cascade = "all,delete",lazy = True)



class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)    #category fk
    name = db.Column(db.String(64), nullable=False)
    base_price = db.Column(db.Integer , nullable=False)
    description = db.Column(db.String(64), nullable=False)
    professional = db.relationship("Professional", backref = 'services',cascade = "all,delete",lazy = True)
    running = db.relationship("Running", backref = 'services',cascade = "all,delete",lazy = True)
    

     

class Running(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)  #it must be not unique as we store all data , back or present.
    s_id = db.Column(db.Integer, db.ForeignKey('services.id') , nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('professional.id'),default='Null')
    c_id = db.Column(db.Integer, db.ForeignKey('category.id') , nullable=False)
    date_time_created = db.Column(db.DateTime, nullable=False)
    date_time_closed = db.Column(db.DateTime, nullable=True)
    ratings = db.Column(db.String(64), nullable=False, default=0)
    status = db.Column(db.String(64), nullable=False, default='pending')
    remarks = db.Column(db.String(64), default=None)

    # customer = db.relationship("User" , backref='service' ,cascade = "all,delete" ,lazy = True)
    # professional = db.relationship()