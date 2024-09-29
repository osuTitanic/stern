
from flask import Blueprint, Response, request
import app.bbcode as bbcode

router = Blueprint('bbcode', __name__)

@router.post('/preview')
def render_bbcode():
    if (input := request.form.get('bbcode')) is None:
        return {
            'error': 400,
            'details': 'The request is missing the required "input" parameter.'
        }, 400

    return Response(
        bbcode.render_html(input),
        status=200,
        mimetype='text/html'
    )
