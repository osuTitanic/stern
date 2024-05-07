
from app.common.database.repositories import users, stats
from app.common.constants import GameMode, COUNTRIES
from app.common.cache import leaderboards
from app.common.database import DBUser

from flask import Blueprint, abort, request

import utils
import math

router = Blueprint('rankings', __name__)

@router.get('/<mode>/<order_type>')
def rankings(mode: str, order_type: str):
    if (mode := GameMode.from_alias(mode)) == None:
        return abort(404)

    if order_type not in ('performance', 'rscore', 'tscore', 'ppv1', 'country', 'clears'):
        return abort(404)

    page = max(1, min(10000, request.args.get('page', default=1, type=int)))
    items_per_page = 50

    # Any two letter country code
    country = request.args.get('country', default=None, type=str)
    country = country.lower() if country else None

    if country == 'xx':
        return abort(404)

    if order_type != 'country':
        leaderboard = leaderboards.top_players(
            mode.value,
            offset=(page - 1) * items_per_page,
            range=items_per_page,
            type=order_type,
            country=country
        )

        # Fetch all users from leaderboard
        users_db = users.fetch_many(
            tuple([user[0] for user in leaderboard]),
            DBUser.stats
        )

        # Sort users based on redis leaderboard
        sorted_users = [
            next(filter(lambda user: id == user.id, users_db))
            for id, score in leaderboard
            if score > 0
        ]

        for user in sorted_users:
            if not user.stats:
                # Create stats if they don't exist
                user.stats = [
                    stats.create(user.id, 0),
                    stats.create(user.id, 1),
                    stats.create(user.id, 2),
                    stats.create(user.id, 3)
                ]

            user.stats.sort(key=lambda s:s.mode)
            utils.sync_ranks(user)

        player_count = leaderboards.player_count(mode.value, order_type, country)
        total_pages = max(1, min(10000, math.ceil(player_count / items_per_page)))

        # Get min/max pages to display for pagination
        max_page_display = max(page, min(total_pages, page + 8))
        min_page_display = max(1, min(total_pages, max_page_display - 9))

        # Fetch top countries for country selection
        top_countries = leaderboards.top_countries(mode)

        order_name = {
            'rscore': 'Ranked Score',
            'tscore': 'Total Score',
            'performance': 'Performance',
            'ppv1': 'PPv1',
            'clears': 'Clears'
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
            order_name=order_name,
            site_title=f'{order_name} Rankings' \
                       f'{f" for {COUNTRIES[country.upper()]}" if country else ""}'
        )

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
