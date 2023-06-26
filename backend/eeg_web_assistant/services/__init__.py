class Service(type):
    _instance = None

    def create(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Service, cls).__call__(*args, **kwargs)
            return cls._instance
        else:
            raise RuntimeError("Service is already created")

    def __call__(cls):
        if cls._instance is None:
            raise RuntimeError("Service is not created")
        return cls._instance
