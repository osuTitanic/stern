
from flask import Blueprint, render_template

router = Blueprint('routes', __name__)

@router.route('/')
def root():
    return render_template(
        'home.html',
        css='home.css'
    )
