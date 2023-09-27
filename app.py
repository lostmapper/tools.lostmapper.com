"""Flask app for various small GIS tools"""

import tempfile

from pathlib import Path
from flask import Flask, render_template, request, send_file

import geopandas
import pandas

app = Flask(__name__)

MERGE_GPX_FORMATS = {
    "gpkg": {"name": "GeoPackage", "extension": "gpkg", "driver": "GPKG"},
    "geojson": {"name": "GeoJSON", "extension": "geojson", "driver": "GeoJSON"},
    "gpx": {"name": "GPS Exchange Format", "extension": "gpx", "driver": "GPX"},
}

MERGE_GPX_COLUMNS = [
    "name",
    "cmt",
    "desc",
    "src",
    "link1_href",
    "link1_text",
    "link1_type",
    "link2_href",
    "link2_text",
    "link2_type",
    "number",
    "type",
    "geometry",
]


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
    return render_template("merge-gpx-tracks.html", formats=MERGE_GPX_FORMATS)


@app.post("/merge-gpx-tracks")
def post_merge_gpx_tracks():
    """Processes Merge GPX Tracks form"""
    files = request.files.getlist("files")
    output_format = request.form["format"]
    extension = MERGE_GPX_FORMATS[output_format]["extension"]
    driver = MERGE_GPX_FORMATS[output_format]["driver"]

    app.logger.info("%i files submitted for %s output", len(files), output_format)
    app.logger.info("%f kilobytes received", request.content_length / 1024)

    merged_tracks = geopandas.GeoDataFrame(
        columns=MERGE_GPX_COLUMNS,
        geometry="geometry",
    )

    for filename in files:
        tracks = geopandas.read_file(filename, layer="tracks")
        merged_tracks = pandas.concat(
            [
                merged_tracks,
                tracks[MERGE_GPX_COLUMNS],
            ]
        )

    if output_format == "gpx":
        merged_tracks["number"] = range(1, len(merged_tracks) + 1)

    with tempfile.TemporaryDirectory() as temp_dir:
        merged_file = str(Path(temp_dir) / f"merged.{extension}")

        merged_tracks.to_file(merged_file, driver=driver)
        return send_file(merged_file)
