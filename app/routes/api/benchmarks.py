
from app.common.database.repositories import benchmarks
from app.models.benchmark import BenchmarkModel

from flask import Blueprint, request

import app

router = Blueprint('benchmarks-api', __name__)

@router.get('/')
def benchmarks_leaderboard():
    with app.session.database.managed_session() as session:
        page = request.args.get(
            'page',
            default=1,
            type=int
        )

        return [
            BenchmarkModel.model_validate(benchmark, from_attributes=True).model_dump()
            for benchmark in benchmarks.fetch_leaderboard(
                limit=50,
                offset=(page - 1) * 50,
                session=session
            )
        ]
