import base

class Hook(base.AbtractBaseTask):
    """Inherit from this class if you want to create hooks with pretty logging"""
    pass

    def operation(self):
        raise NotImplementedError