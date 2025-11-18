from app.extensions import ma
from app.models import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = ma.Email(required=True)
    created_at = ma.DateTime(dump_only=True)  
    
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        
# add a simple login schema to avoid relying on the SQLAlchemy auto schema for authentication
class LoginSchema(ma.Schema):
    email = ma.Email(required=False)  # Make optional since username can be used instead
    username = ma.String(required=False)  # Add username field
    password = ma.String(required=True, load_only=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True) 
login_schema = LoginSchema()