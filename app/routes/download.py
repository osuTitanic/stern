
from flask import Blueprint, render_template

router = Blueprint('download', __name__)

@router.get('/')
def download():
    return render_template(
        'download.html'
    )