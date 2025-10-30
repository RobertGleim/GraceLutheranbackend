

class DevelopmentConfig():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True

class ProductionConfig():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = False