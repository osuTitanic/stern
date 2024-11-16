
from app.models.packs import BeatmapPackModel, BeatmapPackWithEntriesModel
from app.common.database.repositories import packs
from flask import Blueprint, request

import app

router = Blueprint('beatmap-packs', __name__)

@router.get('/packs')
def beatmap_packs():
    with app.session.database.managed_session() as session:
        return [
            BeatmapPackModel.model_validate(pack, from_attributes=True).model_dump()
            for pack in packs.fetch_all(session)
        ]

@router.get('/packs/<category>')
def beatmap_packs_by_category(category: str):
    with app.session.database.managed_session() as session:
        return [
            BeatmapPackModel.model_validate(pack, from_attributes=True).model_dump()
            for pack in packs.fetch_by_category(category, session)
        ]

@router.get('/packs/<category>/<int:pack_id>')
def beatmap_pack(category: str, pack_id: int):
    with app.session.database.managed_session() as session:
        if not (pack := packs.fetch_one(pack_id, session)):
            return {
                'error': 404,
                'details': 'The requested beatmap pack could not be found.'
            }, 404

        return BeatmapPackWithEntriesModel.model_validate(pack, from_attributes=True).model_dump()
