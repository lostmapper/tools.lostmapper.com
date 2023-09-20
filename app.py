"""Flask app for various small GIS tools"""

import tempfile

from pathlib import Path
from flask import Flask, render_template, request, send_file

import geopandas
import pandas

app = Flask(__name__)


@app.route("/")
def index():
    """Renders the index page"""
    return render_template("index.html")


@app.get("/merge-gpx-tracks")
def get_merge_gpx_tracks():
    """Renders Merge GPX Tracks form"""
    return render_template("merge-gpx-tracks.html")


@app.post("/merge-gpx-tracks")
def post_merge_gpx_tracks():
    """Processes Merge GPX Tracks form"""
    merged_tracks = geopandas.GeoDataFrame(
        columns=["name", "type", "geometry"], geometry="geometry"
    )

    files = request.files.getlist("files")

    for filename in files:
        tracks = geopandas.read_file(filename, layer="tracks")
        merged_tracks = pandas.concat(
            [merged_tracks, tracks[["name", "type", "geometry"]]]
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        merged_tracks.to_file(temp_dir / "merged.gpx", driver="GPX")

        return send_file(temp_dir / "merged.gpx")
