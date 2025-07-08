# strategy.py

import statistics

def red_line_strategy(candles):
    """If last two candles closed strongly in one direction."""
    if len(candles) < 3:
        return None
    c1, c2 = candles[-2], candles[-1]

    if c1['close'] > c1['open'] and c2['close'] > c2['open']:
        return {"direction": "buy", "confidence": 0.96, "reason": "Red Line Bullish"}
    elif c1['close'] < c1['open'] and c2['close'] < c2['open']:
        return {"direction": "sell", "confidence": 0.96, "reason": "Red Line Bearish"}
    return None


def double_bollinger_strategy(candles):
    if len(candles) < 5:
        return None

    closes = [c['close'] for c in candles]
    ma = statistics.mean(closes)
    stddev = statistics.stdev(closes)

    upper = ma + 2 * stddev
    lower = ma - 2 * stddev
    last = candles[-1]

    if last['close'] >= upper:
        return {"direction": "sell", "confidence": 0.93, "reason": "Double Bollinger Top"}
    elif last['close'] <= lower:
        return {"direction": "buy", "confidence": 0.93, "reason": "Double Bollinger Bottom"}
    return None


def traffic_light_strategy(candles):
    if len(candles) < 3:
        return None
    green = [c for c in candles[-3:] if c['close'] > c['open']]
    red = [c for c in candles[-3:] if c['close'] < c['open']]

    if len(green) == 3:
        return {"direction": "buy", "confidence": 0.94, "reason": "Traffic Light Green"}
    elif len(red) == 3:
        return {"direction": "sell", "confidence": 0.94, "reason": "Traffic Light Red"}
    return None


def rsi_filter(candles):
    if len(candles) < 14:
        return None
    gains, losses = [], []
    for i in range(-14, -1):
        change = candles[i + 1]['close'] - candles[i]['close']
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14 if losses else 0.01
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    if rsi > 70:
        return {"direction": "sell", "confidence": 0.91, "reason": "RSI Overbought"}
    elif rsi < 30:
        return {"direction": "buy", "confidence": 0.91, "reason": "RSI Oversold"}
    return None


def ema_cross_strategy(candles):
    if len(candles) < 20:
        return None
    closes = [c['close'] for c in candles]

    ema_fast = sum(closes[-5:]) / 5
    ema_slow = sum(closes[-20:]) / 20

    if ema_fast > ema_slow:
        return {"direction": "buy", "confidence": 0.95, "reason": "EMA Fast Above Slow"}
    elif ema_fast < ema_slow:
        return {"direction": "sell", "confidence": 0.95, "reason": "EMA Fast Below Slow"}
    return None


def heiken_ashi_strategy(candles):
    if len(candles) < 3:
        return None

    ha_closes = []
    for c in candles:
        ha_close = (c['open'] + c['high'] + c['low'] + c['close']) / 4
        ha_closes.append(ha_close)

    if ha_closes[-1] > ha_closes[-2] > ha_closes[-3]:
        return {"direction": "buy", "confidence": 0.92, "reason": "Heiken Ashi Bullish"}
    elif ha_closes[-1] < ha_closes[-2] < ha_closes[-3]:
        return {"direction": "sell", "confidence": 0.92, "reason": "Heiken Ashi Bearish"}
    return None


def macd_strategy(candles):
    if len(candles) < 26:
        return None
    closes = [c['close'] for c in candles]
    ema_12 = sum(closes[-12:]) / 12
    ema_26 = sum(closes[-26:]) / 26
    macd_line = ema_12 - ema_26
    signal_line = sum([macd_line] * 9) / 9  # Simple placeholder signal

    if macd_line > signal_line:
        return {"direction": "buy", "confidence": 0.94, "reason": "MACD Bullish Cross"}
    elif macd_line < signal_line:
        return {"direction": "sell", "confidence": 0.94, "reason": "MACD Bearish Cross"}
    return None


# 🧠 Strategy combination logic
def candle_analysis(candles):
    strategies = [
        red_line_strategy,
        double_bollinger_strategy,
        traffic_light_strategy,
        rsi_filter,
        ema_cross_strategy,
        macd_strategy,
        heiken_ashi_strategy
    ]

    votes = []
    for strat in strategies:
        result = strat(candles)
        if result:
            votes.append(result)

    if not votes:
        return {"direction": "none", "confidence": 0}

    # Tally votes
    up_votes = [v for v in votes if v['direction'] == 'buy']
    down_votes = [v for v in votes if v['direction'] == 'sell']

    if len(up_votes) >= len(down_votes):
        top = max(up_votes, key=lambda x: x['confidence'])
    else:
        top = max(down_votes, key=lambda x: x['confidence'])

    if top["confidence"] >= 0.90:
        return top
    return {"direction": "none", "confidence": 0}
