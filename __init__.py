from flask import send_file, jsonify
from flask.helpers import safe_join
from CTFd.utils import get_config
from CTFd.utils.dates import ctf_ended, ctf_started
from CTFd.utils.user import is_verified, is_admin

def load(app):
	@app.route("/OneSignalSDKWorker.js", methods=["GET"])
	def worker():
		filename = safe_join(app.root_path, 'themes', 'tsgctf', 'static', 'OneSignalSDKWorker.js')
		return send_file(filename)

	@app.route("/api/v1/dates", methods=["GET"])
	def dates():
		start = get_config('start')
		end = get_config('end')
		is_started = ctf_started()
		is_ended = ctf_ended()

		return jsonify({
			'success': True,
			'data': {
				'start': start,
				'end': end,
				'is_started': is_started,
				'is_ended': is_ended,
				'is_verified': is_verified() or is_admin(),
			},
		})
