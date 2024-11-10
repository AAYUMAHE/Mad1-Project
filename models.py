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

  # consider username as email  
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  
    services = db.relationship("Services", backref = 'category',cascade = "all,delete" ,lazy = True)


class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256),db.ForeignKey('category.id'), nullable=False )
    s_id = db.Column(db.String(256),db.ForeignKey('services.id'), nullable=False )
         #see category in numbers also if possible
    # service = db.Column(db.String(256), nullable=False)
    pdf = db.Column(db.LargeBinary, nullable=False)
    address = db.Column(db.String(64), nullable=False)
    experience = db.Column(db.String(64), nullable=False)
    pincode = db.Column(db.Integer , nullable=False)



class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)    #category fk
    name = db.Column(db.String(64), nullable=False)
    base_price = db.Column(db.Integer , nullable=False)
    description = db.Column(db.String(64), nullable=False)

     

class Running(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id') , unique=True)
    s_id = db.Column(db.Integer, db.ForeignKey('services.id') , nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey('professional.id'))
    c_id = db.Column(db.Integer, db.ForeignKey('category.id') , nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    date_closed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(64), nullable=False, default='pending')

    # customer = db.relationship("User" , backref='service' ,cascade = "all,delete" ,lazy = True)
    # professional = db.relationship()