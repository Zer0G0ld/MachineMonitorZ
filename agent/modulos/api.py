# modulos/api.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timezone

def create_app(latest_metrics, latest_lock, get_process_details, logger, poll_interval_ref, push_url_ref):
    app = Flask("agent_api")
    CORS(app)

    @app.route("/metrics", methods=["GET"])
    def get_metrics():
        with latest_lock:
            return jsonify(latest_metrics or {"status": "empty"})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "ts": datetime.now(timezone.utc).isoformat()})

    @app.route("/process/<int:pid>", methods=["GET"])
    def process_info(pid):
        try:
            data = get_process_details(pid)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e), "pid": pid})

    @app.route("/config", methods=["POST"])
    def set_config():
        data = request.json or {}
        if "poll_interval" in data:
            try:
                val = int(data["poll_interval"])
                poll_interval_ref[0] = max(1, val)
                logger.info(f"Poll interval alterado para {poll_interval_ref[0]}s")
            except:
                pass
        if "push_url" in data:
            push_url_ref[0] = data["push_url"]
            logger.info(f"PUSH_URL alterado para {push_url_ref[0]}")
        return jsonify({"ok": True, "poll_interval": poll_interval_ref[0], "push_url": push_url_ref[0]})

    return app
