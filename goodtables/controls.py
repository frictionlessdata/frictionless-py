from .metadata import Metadata


class Control(Metadata):

    # Expand

    def expand(self):
        pass


class LocalControl(Metadata):
    pass


class RemoteControl(Metadata):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'httpSession': {},
            'httpStream': {'type': 'boolean'},
            'httpTimeout': {'type': 'number'},
        },
    }

    # Expand

    def expand(self):
        self.setdetault('httpStream', True)


class StreamControl(Metadata):
    pass


class TextControl(Metadata):
    pass
