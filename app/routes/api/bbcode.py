
from flask import Blueprint, Response, request
import app.bbcode as bbcode

router = Blueprint('bbcode', __name__)

@router.post('/preview')
def render_bbcode():
    if (input := request.form.get('bbcode')) is None:
        return Response('', 400)

    return Response(
        bbcode.formatter.format(input),
        status=200,
        mimetype='text/html'
    )
