"""Kullanici dostu web dashboard — portfoy, sinyaller, pozisyonlar (Flask)."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .analyzer import combine
from .binance_client import BinanceFutures
from .config import ROOT, load_config
from .main import run_once
from .minimax import MiniMaxClient
from .strategy import evaluate

app = Flask(__name__, static_folder=None)
_CFG = load_config()
_WEB = Path(__file__).resolve().parent / "web"

# tarama durumu (ayni anda tek tarama)
_scan_lock = threading.Lock()
_scan_state = {"running": False, "error": None}


def _data_path(name: str) -> Path:
    report_dir = _CFG.run.get("report_dir", "data")
    p = Path(report_dir)
    base = p if p.is_absolute() else ROOT / p
    return base / name


def _read_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


@app.after_request
def _no_cache(resp):
    """Tarayicinin eski HTML/JS'i onbellekten gostermesini engelle."""
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/")
def index():
    resp = send_from_directory(_WEB, "index.html")
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/state")
def api_state():
    signals = _read_json(_data_path("signals.json"))
    state = _read_json(_data_path(Path(_CFG.run.get("state_file", "data/state.json")).name))
    return jsonify({
        "ai_enabled": _CFG.ai_enabled,
        "scan": _scan_state,
        "signals": signals,
        "open_positions": state.get("open_positions", []),
        "closed_trades": state.get("closed_trades", []),
        "balance": state.get("balance"),
        "start_balance": state.get("start_balance"),
        "state_updated_at": state.get("updated_at"),
    })


def _do_scan(no_ai: bool):
    try:
        run_once(_CFG, no_ai=no_ai, verbose=False)
    except Exception as e:  # noqa: BLE001
        _scan_state["error"] = str(e)
    finally:
        _scan_state["running"] = False


@app.route("/api/scan", methods=["POST"])
def api_scan():
    if not _scan_lock.acquire(blocking=False):
        return jsonify({"ok": False, "error": "Tarama zaten suruyor"}), 409
    try:
        if _scan_state["running"]:
            return jsonify({"ok": False, "error": "Tarama zaten suruyor"}), 409
        _scan_state["running"] = True
        _scan_state["error"] = None
        no_ai = not _CFG.ai_enabled
        threading.Thread(target=lambda: (_do_scan(no_ai), _scan_lock.release()), daemon=True).start()
        return jsonify({"ok": True})
    except Exception:
        _scan_lock.release()
        raise


def _suggest_levels(direction: str, price: float, atr: float) -> dict:
    """ATR tabanli onerilen giris/stop/hedef (paper_trader ile ayni mantik)."""
    d = direction if direction in ("LONG", "SHORT") else "LONG"
    sl_mult = float(_CFG.risk.get("atr_sl_mult", 1.5))
    rr = float(_CFG.risk.get("risk_reward", 1.8))
    dist = sl_mult * atr
    if d == "LONG":
        sl, tp = price - dist, price + dist * rr
    else:
        sl, tp = price + dist, price - dist * rr
    return {
        "direction": d,
        "indicative": direction == "NEUTRAL",
        "entry": price,
        "stop_loss": sl,
        "take_profit": tp,
        "risk_reward": rr,
    }


@app.route("/api/analyze")
def api_analyze():
    """Tek bir coini anlik analiz et (arama cubugu)."""
    quote = _CFG.market.get("quote_asset", "USDT")
    symbol = request.args.get("symbol", "").strip().upper().replace(" ", "")
    if not symbol:
        return jsonify({"ok": False, "error": "Coin sembolu girin (orn. DOGE)"}), 400
    if not symbol.endswith(quote):
        symbol += quote

    client = BinanceFutures(_CFG.binance_fapi_base)
    try:
        df = client.klines(
            symbol,
            _CFG.market.get("timeframe", "15m"),
            int(_CFG.market.get("klines_limit", 200)),
        )
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": f"{symbol} verisi alinamadi: {e}"}), 502

    ta = evaluate(symbol, df, _CFG.strategy)
    if ta is None:
        return jsonify({"ok": False, "error": f"{symbol} icin yeterli mum verisi yok"}), 422

    ai_payload = None
    ai_verdict = None
    if _CFG.ai_enabled:
        ai_verdict = MiniMaxClient(
            _CFG.minimax_api_key, _CFG.minimax_base_url, _CFG.minimax_model
        ).analyze(symbol, ta.snapshot, ta.direction)
        if ai_verdict.ok:
            ai_payload = {
                "direction": ai_verdict.direction,
                "confidence": ai_verdict.confidence,
                "reason": ai_verdict.reason,
            }

    dec = combine(ta, ai_verdict, _CFG.strategy)

    return jsonify({
        "ok": True,
        "symbol": symbol,
        "timeframe": _CFG.market.get("timeframe", "15m"),
        "price": ta.price,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "ta_direction": ta.direction,
        "ta_score": ta.score,
        "ai_enabled": _CFG.ai_enabled,
        "ai": ai_payload,
        "note": dec.note,
        "votes": ta.votes,
        "indicators": ta.snapshot,
        "levels": _suggest_levels(dec.direction, ta.price, ta.atr),
    })


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Scalp Bot dashboard")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    print(f"Dashboard: http://{args.host}:{args.port}  (Ctrl+C ile cik)")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
