
from flask_login import login_required
from flask import Blueprint

router = Blueprint('profile-settings', __name__)

@router.get('/profile')
@login_required
def profile_settings():
    ...
