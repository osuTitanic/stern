
from matplotlib.backends.backend_agg import FigureCanvasAgg
from flask import Blueprint, Response, send_file, abort
from datetime import datetime, timedelta
from io import BytesIO

from app.common.database.repositories import usercount
from app.common.database import DBUserActivity
from app.common.helpers import caching

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

router = Blueprint("activity", __name__)

# Use Anti-Grain Geometry backend (non-GUI backend)
mpl.use('Agg')

def calculate_peak_x(
    n: DBUserActivity,
    smallest: DBUserActivity,
    largest: DBUserActivity
) -> datetime:
    """Used to calculate the x position of peak text, so that it doesnt exit the chart box."""
    time_range = largest.time - smallest.time
    return max(
        smallest.time,
        min(
            # Add offset to time
            n.time,
            largest.time - time_range * 0.15
        )
    )

@caching.ttl_cache(ttl=60)
def generate_activity_chart(width: int, height: int) -> bytes:
    usercounts = usercount.fetch_range(
        datetime.now() - timedelta(hours=24),
        datetime.now()
    )

    if not usercounts:
        return abort(500, 'User activity is empty. Please contact an administrator!')

    peak = max(usercounts, key=lambda x: x.count)

    # Define width & height
    plt.figure(figsize=np.array([width, height]) / 100)
    plt.tight_layout()

    # Define plot
    plt.plot(
        [uc.time for uc in usercounts],
        [uc.total_users for uc in usercounts],
        linestyle='-',
        color='#9096bc'
    )

    # Remove lables
    plt.tick_params(
        direction="in",
        labelbottom=False,
        labelleft=False
    )

    # Increase y height
    plt.ylim(top=peak.count + (peak.count * 0.5))

    # Prevent text overflow
    plt.autoscale(False)

    if peak.count > 0:
        # Add peak text
        plt.annotate(
            text=f'Peak: {peak.count} {"users" if peak.count > 1 else "user"}',
            fontsize=8,
            xy=(
                # X Offset
                calculate_peak_x(
                    peak,
                    usercounts[-1],
                    usercounts[0]
                ),
                # Y Offset
                peak.count - peak.count * 0.4
            ),
            zorder=2
        )

        # Add peak point
        plt.scatter(
            peak.time, peak.count,
            c='blue',
            s=12,
            zorder=4
        )

    # Enable grid layout
    plt.grid(
        True,
        color='#ffd0f6'
    )

    # Render the figure to a PNG image
    canvas = FigureCanvasAgg(plt.gcf())
    buffer = BytesIO()
    canvas.print_figure(
        buffer,
        format='png',
        pad_inches=0.015,
        bbox_inches='tight'
    )
    buffer.seek(0)
    return buffer.read()

@router.get('/image')
def user_activity_chart(
    width: int = 600,
    height: int = 90
) -> Response:
    return send_file(
        BytesIO(generate_activity_chart(width, height)),
        mimetype='image/png',
        as_attachment=False,
        download_name='useractivity.png'
    )
