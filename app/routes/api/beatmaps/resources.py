
from flask import Blueprint, Response, send_file, request
from flask_pydantic import validate

import app.session as session
import zipfile
import utils
import io

router = Blueprint('resources', __name__)

def remove_video_from_osz(osz: bytes) -> bytes:
    video_extensions = [
        ".wmv", ".flv", ".mp4", ".avi", ".m4v"
    ]

    with zipfile.ZipFile(io.BytesIO(osz), 'r') as osz_file:
        files_to_keep = [
            item for item in osz_file.namelist()
            if not any(item.lower().endswith(ext) for ext in video_extensions)
        ]

        output = io.BytesIO()

        with zipfile.ZipFile(output, 'w') as new_osz:
            for file in files_to_keep:
                new_osz.writestr(file, osz_file.read(file))

        return output.getvalue()

@router.get('/osz/<set_id>')
@validate()
def internal_osz(set_id: int):
    osz = session.storage.get_osz_internal(set_id)

    if not osz:
        return Response(status=404)

    no_video = request.args.get(
        'noVideo',
        default=False,
        type=bool
    )

    if no_video:
        osz = remove_video_from_osz(osz)

    return send_file(
        io.BytesIO(osz),
        as_attachment=True,
        download_name=f'{set_id}.osz',
        mimetype='application/octet-stream'
    )

@router.get('/osz2/<set_id>')
@validate()
def internal_osz2(set_id: int):
    osz2 = session.storage.get_osz2_internal(set_id)

    if not osz2:
        return Response(status=404)

    return send_file(
        io.BytesIO(osz2),
        as_attachment=True,
        download_name=f'{set_id}.osz2',
        mimetype='application/octet-stream'
    )

@router.get('/osu/<beatmap_id>')
@validate()
def internal_beatmap_file(beatmap_id: int):
    osu = session.storage.get_beatmap_internal(beatmap_id)

    if not osu:
        return Response(status=404)

    return send_file(
        io.BytesIO(osu),
        as_attachment=True,
        download_name=f'{beatmap_id}.osu',
        mimetype='text/plain'
    )

@router.get('/mt/<set_id>')
@validate()
def internal_beatmap_thumbnail(set_id: int):
    mt = session.storage.get_background_internal(set_id)

    if not mt:
        return Response(status=404)

    large = request.args.get('large')

    if large == None:
        # Downscale thumbnail by default
        mt = utils.resize_image(
            mt,
            target_width=80,
            target_height=60
        )

    return send_file(
        io.BytesIO(mt),
        mimetype='image/jpeg'
    )

@router.get('/mp3/<set_id>')
@validate()
def internal_beatmap_audio(set_id: int):
    mp3 = session.storage.get_mp3_internal(set_id)

    if not mp3:
        return Response(status=404)

    return send_file(
        io.BytesIO(mp3),
        mimetype='audio/mpeg'
    )
