

from matplotlib.backends.backend_agg import FigureCanvasAgg
from datetime import datetime, timedelta
from flask import Blueprint, send_file
from io import BytesIO
from copy import copy

from app.common.database.repositories import usercount
from app.common.database import DBUserCount

import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('agg')

router = Blueprint("activity", __name__)

def calculate_peak_x(
    n: DBUserCount,
    smallest: DBUserCount,
    largest: DBUserCount
) -> datetime:
    """Used to calculate the x position of peak text, so that it doesnt exit the chart box."""
    return max(
        smallest.time,
        min(
            # Add offset to time
            n.time - timedelta(seconds=750),
            largest.time
        )
    )

@router.get('/useractivity')
def user_activity_chart(
    width: int = 600,
    height: int = 90
):
    usercounts = usercount.fetch_range(
        datetime.now() - timedelta(hours=24),
        datetime.now()
    )

    peak = max(usercounts, key=lambda x: x.count)

    # Define width & height
    plt.figure(figsize=np.array([width, height]) / 100)
    plt.tight_layout()

    # Define plot
    plot = plt.plot(
        [uc.time for uc in usercounts],
        [uc.count for uc in usercounts],
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
    plt.ylim(
        top=peak.count + (peak.count * 0.5),
        bottom=0
    )

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
        )
    )

    # Add peak point
    plt.scatter(
        peak.time, peak.count,
        c='blue',
        s=15
    )

    # Enable grid layout
    plt.grid(True, color='#ffd0f6')

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

    return send_file(
        buffer,
        mimetype='image/png',
        as_attachment=False,
        download_name='useractivity.png'
    )
