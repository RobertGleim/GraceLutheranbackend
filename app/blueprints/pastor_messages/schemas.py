from app.extensions import ma
from app.models import PastorMessage


class PastorMessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PastorMessage
        include_fk = True
        load_instance = True
        
        
pastor_message_schema = PastorMessageSchema()
pastor_messages_schema = PastorMessageSchema(many=True)