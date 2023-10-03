
from flask import Blueprint

router = Blueprint('routes', __name__)

@router.route('/')
def root():
    return 'Hi.'
