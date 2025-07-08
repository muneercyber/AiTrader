# Your advanced strategies here (simplified example with threshold tuning)
def candle_analysis(candles):
    if len(candles) < 4:
        return {"direction": "none", "confidence": 0}

    last = candles[-1]
    prev = candles[-2]

    # Simple bullish pattern example
    if last['close'] > last['open'] and prev['close'] > prev['open']:
        return {"direction": "up", "confidence": 0.92}

    # Simple bearish pattern example
    if last['close'] < last['open'] and prev['close'] < prev['open']:
        return {"direction": "down", "confidence": 0.91}

    return {"direction": "none", "confidence": 0}
