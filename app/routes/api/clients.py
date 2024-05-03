
from app.common.database import releases
from app.models import Client
from flask import Blueprint

router = Blueprint('clients', __name__)

@router.get('/')
def fetch_clients():
    return [
        Client.model_validate(client, from_attributes=True).model_dump()
        for client in releases.fetch_all()
    ]
