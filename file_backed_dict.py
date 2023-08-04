import json


class FileBackedDict:
    def __init__(self, filename, data = {}):
        self._filename = filename
        self._data = data
        self._write_to_file()

    def __setitem__(self, key, value):
        self._data[key] = value
        self._write_to_file()

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]
        self._write_to_file()

    def __contains__(self, key):
        return key in self._data

    def _write_to_file(self):
        with open(self._filename, 'w') as f:
            f.write(json.dumps(self._data, indent=2))


if __name__ == '__main__':
    data = FileBackedDict('data.json')
    data['key'] = 'value'
    print(data['key'])
