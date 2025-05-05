
from app.common.database.repositories import users, stats, beatmaps
from app.common.constants import GameMode, COUNTRIES
from app.common.database import DBUser, DBStats
from app.common.cache import leaderboards

from flask import Blueprint, abort, request
from sqlalchemy.orm import Session
from typing import List

import utils
import time
import math
import app

router = Blueprint('rankings', __name__)

valid_order_types = (
    'performance', 'rscore',  'country',
    'ppv1', 'tscore', 'clears', 'leader'
)

@router.get('/<mode>/<order_type>')
def rankings(mode: str, order_type: str):
    if (mode := GameMode.from_alias(mode)) == None:
        return abort(404)

    if order_type not in valid_order_types:
        return abort(404)

    page = max(1, min(10000, request.args.get('page', default=1, type=int)))
    items_per_page = 50

    # Any two letter country code
    country = request.args.get('country', default=None, type=str)
    country = country.lower() if country else None

    if country == 'xx':
        return abort(404)

    if country and country.upper() not in COUNTRIES:
        return abort(404)

    if order_type != 'country':
        return render_rankings_page(
            order_type, country,
            mode, page,
            items_per_page
        )

    return render_country_page(
        items_per_page,
        page, mode
    )

def render_rankings_page(
    order_type: str,
    country: str,
    mode: GameMode,
    page: int,
    items_per_page: int,
) -> str:
    with app.session.database.managed_session() as session:
        jumpto = request.args.get('jumpto', default=None)

        if jumpto and (user := users.fetch_by_name_case_insensitive(jumpto, session)):
            # Change the page to where the user is
            user_rank = leaderboards.rank(
                user.id,
                mode.value,
                order_type,
                country
            )
            page = math.ceil(user_rank / items_per_page)

        leaderboard = leaderboards.top_players(
            mode.value,
            offset=(page - 1) * items_per_page,
            range=items_per_page,
            type=order_type,
            country=country
        )

        # Fetch all users from leaderboard
        users_db = users.fetch_many(
            [user[0] for user in leaderboard],
            DBUser.stats,
            session=session
        )

        # Sort users based on redis leaderboard
        sorted_users = [
            next(filter(lambda user: id == user.id, users_db))
            for id, score in leaderboard
            if score > 0
        ]

        # Ensure all users have stats & they are sorted
        ensure_user_stats(sorted_users, session)

        if (time.time() - app.session.last_rank_sync) > 30:
            # Sync ranks from cache to database in background once in a while
            app.session.executor.submit(sync_ranks, sorted_users, mode)
            app.session.last_rank_sync = time.time()

        player_count = leaderboards.player_count(mode.value, order_type, country)
        total_pages = max(1, min(10000, math.ceil(player_count / items_per_page)))

        # Get min/max pages to display for pagination
        max_page_display = max(page, min(total_pages, page + 8))
        min_page_display = max(1, min(total_pages, max_page_display - 9))

        # Fetch top countries for country selection
        top_countries = leaderboards.top_countries(mode)

        order_name = {
            'performance': 'Performance',
            'rscore': 'Ranked Score',
            'tscore': 'Total Score',
            'clears': 'Clears',
            'ppv1': 'PPv1'
        }[order_type.lower()]

        return utils.render_template(
            'rankings.html',
            css='rankings.css',
            title=f'{order_name} Rankings - Titanic',
            mode=mode,
            page=page,
            country=country,
            order_type=order_type,
            total_pages=total_pages,
            leaderboard=sorted_users,
            top_countries=top_countries,
            max_page_display=max_page_display,
            min_page_display=min_page_display,
            items_per_page=items_per_page,
            canonical_url=request.base_url,
            order_name=order_name,
            session=session,
            jumpto=jumpto,
            total_beatmaps=(
                beatmaps.fetch_count_with_leaderboards(mode, session)
                if order_type == 'clears' else 0
            ),
            site_title=(
                f'{order_name} Rankings'
                f'{f" for {COUNTRIES[country.upper()]}" if country else ""}'
            )
        )

def render_country_page(
    items_per_page: int,
    page: int,
    mode: GameMode
) -> str:
    # Get country ranking
    leaderboard = [country for country in leaderboards.top_countries(mode) if country['name'] != 'xx']
    leaderboard = leaderboard[(page - 1)*items_per_page:(page - 1)*items_per_page + items_per_page]

    country_count = len(leaderboard)
    total_pages = max(1, min(10000, math.ceil(country_count / items_per_page)))

    # Get min/max pages to display for pagination
    max_page_display = max(page, min(total_pages, page + 8))
    min_page_display = max(1, min(total_pages, max_page_display - 9))

    return utils.render_template(
        'country.html',
        css='country.css',
        title='Country Rankings - Titanic',
        mode=mode,
        page=page,
        total_pages=total_pages,
        leaderboard=leaderboard,
        max_page_display=max_page_display,
        min_page_display=min_page_display,
        items_per_page=items_per_page,
        site_title='Country Rankings'
    )

def ensure_user_stats(users: List[DBUser], session: Session) -> None:
    for user in users:
        user.stats = user.stats or create_user_stats(user, session)
        user.stats.sort(key=lambda s:s.mode)

def sync_ranks(users: List[DBUser], mode: GameMode) -> None:
    with app.session.database.managed_session() as session:
        for user in users:
            utils.sync_ranks(user, mode.value, session)

def create_user_stats(user: DBUser, session) -> List[DBStats]:
    return [
        stats.create(user.id, 0, session),
        stats.create(user.id, 1, session),
        stats.create(user.id, 2, session),
        stats.create(user.id, 3, session)
    ]
