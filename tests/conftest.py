def pytest_configure(config):
    config.addinivalue_line("markers", "model: runs the real YOLO model (slower)")
