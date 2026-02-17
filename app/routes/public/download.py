
from app.common.database import releases
from flask import Blueprint, request, redirect
from flask_login import current_user
from collections import defaultdict

import utils

router = Blueprint('download', __name__)

@router.get('/')
def download():
    client_releases = releases.fetch_all()
    sorted_releases = defaultdict(list)

    for release in client_releases:
        sorted_releases[release.category].append(release)

    return utils.render_template(
        'download.html',
        css='download.css',
        title="Download - Titanic",
        site_title="Download",
        site_description="Let's get you started! Choose and download your preferred version of osu!.",
        releases=sorted_releases
    )

@router.get('/timeline')
def download_timeline():
    if not current_user.is_authenticated or not current_user.is_admin:
        # Disable timeline for non-admins until this is ready
        return redirect('/download')

    # TODO: Make this configurable
    from_year = 2007
    to_year = 2016

    daily_heatmap = releases.fetch_heatmap(from_year, to_year)
    monthly_heatmap = defaultdict(int)
    available_years = set()

    for (year, month, day), count in daily_heatmap.items():
        monthly_heatmap[(year, month)] += count
        available_years.add(year)

    # Determine default selected year
    selected_year = (
        max(available_years)
        if available_years else None
    )

    # If valid, choose requested year from query parameters
    requested_year = request.args.get('year', type=int)

    if requested_year in available_years:
        selected_year = requested_year

    # Build context for timeline template
    sorted_available_years = sorted(available_years)
    timeline_years = build_timeline_years(sorted_available_years, monthly_heatmap)

    return utils.render_template(
        'download_timeline.html',
        css='download.css',
        title="Download Timeline - Titanic",
        site_title="Download Timeline",
        site_description="A timeline of all osu! releases, presented in a wayback-machine-like format",
        heatmap=daily_heatmap,
        monthly_heatmap=monthly_heatmap,
        timeline_years=timeline_years,
        selected_year=selected_year,
        from_year=from_year,
        to_year=to_year
    )

def intensity_level(value: int, max_value: int) -> int:
    if value <= 0:
        return 0

    if max_value <= 0:
        return 1

    level = (value * 10 + max_value - 1) // max_value
    return max(1, min(10, level))

def build_timeline_years(available_years: list[int], monthly_heatmap: dict) -> list[dict]:
    max_monthly_count = max(monthly_heatmap.values(), default=0)
    timeline_years = []

    for year in available_years:
        months = []
        total = 0

        for month in range(1, 13):
            count = monthly_heatmap.get(
                (year, month), 0
            )
            intensity = intensity_level(
                count, max_monthly_count
            )
            months.append({
                'month': month,
                'count': count,
                'level': intensity
            })
            total += count

        timeline_years.append({
            'year': year,
            'months': months,
            'total': total
        })

    return timeline_years
