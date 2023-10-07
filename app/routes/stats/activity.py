
from app.external import PHP
from flask import Blueprint

router = Blueprint("activity", __name__)

@router.get('/useractivity')
def user_activity_chart():
    return PHP().get_raw("echo 'Hello World!';")
