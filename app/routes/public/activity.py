
from app.common.database.repositories import usercount
from app.common.helpers import caching
from utils import hex_to_rgba

from flask import Blueprint, Response, send_file, abort
from datetime import datetime, timedelta
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

router = Blueprint("activity", __name__)

BACKGROUND_COLOR = hex_to_rgba('#f0ecfa')
GRID_COLOR = hex_to_rgba('#dddddd')
OSU_FILL_COLOR = hex_to_rgba('#ffe8fa')
OSU_LINE_COLOR = hex_to_rgba('#ffd0f6')
IRC_FILL_COLOR = hex_to_rgba('#dfe2f4')
IRC_LINE_COLOR = hex_to_rgba('#9096bc')
GAMES_COLOR = hex_to_rgba('#ef8e03')

# Use non-gui backend
matplotlib.use('Agg')

@caching.ttl_cache(ttl=60)
def generate_activity_chart(width: int, height: int, dpi: int = 100) -> bytes:
    # Fetch last 24 hours of data
    activity_entries = usercount.fetch_range(
        datetime.now() - timedelta(hours=24),
        datetime.now()
    )

    if not activity_entries:
        abort(500, 'User activity is empty. Please contact an administrator!')

    # Parse data into separate arrays & then interpolate
    # data to 1440 points, i.e. one per minute
    irc = [uc.irc_count for uc in activity_entries]
    osu = [uc.osu_count for uc in activity_entries]
    games = [uc.mp_count for uc in activity_entries]

    # If we have fewer data points, interpolate to 1440
    if len(activity_entries) < 1440:
        x_original = np.linspace(0, 1440, len(activity_entries))
        x_target = np.arange(0, 1440)
        irc = np.interp(x_target, x_original, irc).astype(int).tolist()
        osu = np.interp(x_target, x_original, osu).astype(int).tolist()
        games = np.interp(x_target, x_original, games).astype(int).tolist()

    # If we have more data points, sample down to 1440
    elif len(activity_entries) > 1440:
        step = len(activity_entries) / 1440
        irc = [irc[int(i * step)] for i in range(1440)]
        osu = [osu[int(i * step)] for i in range(1440)]
        games = [games[int(i * step)] for i in range(1440)]

    # Reverse all arrays to have oldest data at the beginning
    irc.reverse()
    osu.reverse()
    games.reverse()

    # Find the peak
    total_users = [osu[i] + irc[i] for i in range(len(osu))]
    highest_val = max(total_users) if total_users else 0
    highest_idx = total_users.index(highest_val) if highest_val > 0 else 0

    # Calculate y-axis maximum with proportional padding
    padding = max(10, int(highest_val * 0.2))
    high = ((highest_val + padding) // 10) * 10

    # Create figure with specified dimensions & add axes
    fig = plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax = fig.add_axes([0, 0.03, 0.995, 0.96])
    ax.set_facecolor(BACKGROUND_COLOR)

    # Set axis limits
    ax.set_xlim(0, 1440)
    ax.set_ylim(0, high)

    # X-axis range for plotting
    x = np.arange(0, 1440)

    # Set major ticks (24 ticks for x-axis, 15 for y-axis)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(60))
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(15))

    # Draw 4x2 grid manually at specific positions
    for x_grid in np.arange(0, 1441, 360):
        ax.axvline(x_grid, color=GRID_COLOR, linewidth=0.8, zorder=1)

    for y_grid in np.arange(0, high + 1, high / 3):
        ax.axhline(y_grid, color=GRID_COLOR, linewidth=0.8, zorder=1)

    # Remove minor ticks
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.yaxis.set_zorder(30)
    ax.xaxis.set_zorder(30)

    # Plot osu! users
    ax.fill_between(x, 0, osu, color=OSU_FILL_COLOR, linewidth=0, zorder=1)
    ax.plot(x, osu, color=OSU_LINE_COLOR, linewidth=1, zorder=2)

    # Plot IRC users
    ax.fill_between(x, 0, irc, color=IRC_FILL_COLOR, linewidth=0, zorder=3)
    ax.plot(x, irc, color=IRC_LINE_COLOR, linewidth=0.25, zorder=4, solid_capstyle='round')

    # Plot multiplayer games
    ax.fill_between(x, 0, games, color=GAMES_COLOR, linewidth=0, zorder=4)
    ax.plot(x, games, color=GAMES_COLOR, linewidth=1, zorder=5)

    osu_at_peak = osu[highest_idx]
    ax.scatter([highest_idx], [osu_at_peak], s=12, color='blue', alpha=0.3, zorder=21)

    peak_text = f"Peak: {highest_val} users"
    ha = "right" if highest_idx > 700 else "left"
    offset = -2 if highest_idx > 700 else 2

    # Add peak text showing total users
    ax.text(
        highest_idx + offset,
        osu_at_peak + offset,
        peak_text,
        fontsize=7,
        color='black',
        ha=ha,
        va='top',
        zorder=20,
        bbox={
            'facecolor': BACKGROUND_COLOR,
            'boxstyle': 'square,pad=0.1',
            'edgecolor': 'none'
        }
    )

    # Hide axis labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Configure tick appearance
    ax.tick_params(
        axis='x',
        which='major',
        length=2,
        width=0.8,
        color='black',
        direction='in',
        bottom=True,
        top=False,
        pad=0
    )
    ax.tick_params(
        axis='y',
        which='major',
        length=1.8,
        width=0.8,
        color='black',
        direction='in',
        left=True,
        right=False,
        pad=0
    )

    # Make every 6th x-axis tick and every 5th y-axis tick longer
    for i, tick in enumerate(ax.xaxis.get_major_ticks()):
        if (i - 1) % 6 == 0:
            tick.tick1line.set_markersize(3.6)

    for i, tick in enumerate(ax.yaxis.get_major_ticks()):
        if (i + 1) % 5 == 0:
            tick.tick1line.set_markersize(3.6)

    # Show only left and bottom spines
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color('black')
    ax.spines['left'].set_linewidth(1)

    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('black')
    ax.spines['bottom'].set_linewidth(1)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Save to bytes buffer
    buf = BytesIO()
    plt.savefig(
        buf,
        format='png', dpi=dpi,
        facecolor=fig.get_facecolor(), 
        edgecolor='none', pad_inches=0
    )
    buf.seek(0)
    plt.close(fig)
    return buf.read()

@router.get('/image')
def user_activity_chart(
    width: int = 460,
    height: int = 70
) -> Response:
    return send_file(
        BytesIO(generate_activity_chart(width, height)),
        mimetype='image/png',
        as_attachment=False,
        download_name='useractivity.png'
    )
