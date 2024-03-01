state = 0


def hello_task():
    global state

    print(f"HeatBeat: {'Ping...' if state else 'Pong...'}")
    state = 1 - state
