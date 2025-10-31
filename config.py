import os

class DevelopmentConfig():
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    CACHE_TYPE = 'simpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

class ProductionConfig():
  
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db'
    SECRET_KEY = os.getenv('SECRET_KEY') or 'super secret key'
    CACHE_TYPE = 'simpleCache'

class TestingConfig():
  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_church.db'
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test_secret_key'
    CACHE_TYPE = 'null'
    CACHE_DEFAULT_TIMEOUT = 0
