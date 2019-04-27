from flask import send_file
from flask.helpers import safe_join

def load(app):
	@app.route("/OneSignalSDKWorker.js", methods=["GET"])
	def worker():
		filename = safe_join(app.root_path, 'themes', 'tsgctf', 'static', 'OneSignalSDKWorker.js')
		return send_file(filename)
