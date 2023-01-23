class KoGekkoError(Exception):
    pass


class KoGekkoBackendError(KoGekkoError):
    pass


class KoGekkoInputError(KoGekkoError):
    pass


class KoGekkoRemoteError(KoGekkoError):
    pass
