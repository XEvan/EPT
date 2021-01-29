import os

from app.app import App


class FotaOtaTester(App):
    def __init__(self):
        super(FotaOtaTester, self).__init__()
        self.name = "FotaOtaTester"
        self.business_type = "FotaOtaTester"
        path = os.path.abspath(os.path.split(__file__)[0])
        self.mount_aw_provider(path)
