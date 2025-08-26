from flask import Blueprint
from . import auth, products, sales, customers, suppliers, returns, reports

main_blueprint = Blueprint('main', __name__)

# استيراد جميع المسارات
from .auth import *
from .products import *
from .sales import *
from .customers import *
from .suppliers import *
from .returns import *
from .reports import *
