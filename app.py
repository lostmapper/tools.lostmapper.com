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


@app.get("/")
def index():
    """Renders the Welcome page"""
    return render_template("index.html")


@app.get("/about")
def about():
    """Renders the About page"""
    return render_template("about.html")


@app.get("/merge-gpx-tracks")
def get_merge_gpx_tracks():
    """Renders Merge GPX Tracks form"""
    return render_template("merge-gpx-tracks.html", formats=formats)


@app.post("/merge-gpx-tracks")
def post_merge_gpx_tracks():
    """Processes Merge GPX Tracks form"""
    files = request.files.getlist("files")
    output_format = request.form["format"]
    extension = formats[output_format]["extension"]
    driver = formats[output_format]["driver"]

    app.logger.info("%i files submitted for %s output", len(files), output_format)
    app.logger.info("%f kilobytes received", request.content_length / 1024)

    merged_tracks = geopandas.GeoDataFrame(
        columns=["name", "type", "geometry"], geometry="geometry"
    )

    for filename in files:
        tracks = geopandas.read_file(filename, layer="tracks")
        merged_tracks = pandas.concat(
            [merged_tracks, tracks[["name", "type", "geometry"]]]
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        merged_file = Path(temp_dir) / f"merged.{extension}"

        merged_tracks.to_file(merged_file, driver=driver)
        return send_file(merged_file)
