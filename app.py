"""Flask app for various small GIS tools"""

import tempfile

from pathlib import Path
from flask import Flask, render_template, request, send_file

import geopandas
import pandas

app = Flask(__name__)

formats = {
    "gpkg": {"name": "GeoPackage", "extension": "gpkg", "driver": "GPKG"},
    "geojson": {"name": "GeoJSON", "extension": "geojson", "driver": "GeoJSON"},
    "gpx": {"name": "GPS Exchange Format", "extension": "gpx", "driver": "GPX"},
}


@app.route("/")
def index():
    """Renders the index page"""
    return render_template("index.html")


@app.get("/merge-gpx-tracks")
def get_merge_gpx_tracks():
    """Renders Merge GPX Tracks form"""
    return render_template("merge-gpx-tracks.html", formats=formats)


@app.post("/merge-gpx-tracks")
def post_merge_gpx_tracks():
    """Processes Merge GPX Tracks form"""
    files = request.files.getlist("files")
    extension = formats[request.form["format"]]["extension"]
    driver = formats[request.form["format"]]["driver"]

    merged_tracks = geopandas.GeoDataFrame(
        columns=["name", "type", "geometry"], geometry="geometry"
    )

    for filename in files:
        tracks = geopandas.read_file(filename, layer="tracks")
        merged_tracks = pandas.concat(
            [merged_tracks, tracks[["name", "type", "geometry"]]]
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        merged_filename = f"merged.{extension}"
        merged_file = Path(temp_dir) / merged_filename

        merged_tracks.to_file(merged_file, driver=driver)
        return send_file(merged_file)
