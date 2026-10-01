"""Isolate KiCad's native DLLs from FreeCAD using a local JSON pipe.

On platforms with compatible native libraries, importing pcbnew directly remains
supported. Windows FreeCAD uses the explicitly selected KiCad Python subprocess;
the actual KiCad API performs every operation, including integer polygon Boolean
operations. No network, geometry approximation or foreign DLL copying is used.
"""
import atexit
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys


def serve():
    import pcbnew
    objects = {0: pcbnew}
    counter = 0

    def encode(value):
        nonlocal counter
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if type(value).__name__ == 'UTF8':
            return str(value)
        if isinstance(value, (list, tuple)):
            return [encode(item) for item in value]
        counter += 1
        objects[counter] = value
        return {'object': counter}

    def decode(value):
        if isinstance(value, dict) and 'object' in value:
            return objects[value['object']]
        if isinstance(value, list):
            return [decode(item) for item in value]
        return value

    for line in sys.stdin:
        try:
            request = json.loads(line)
            value = objects[request['object']]
            operation = request['operation']
            if operation == 'get':
                result = getattr(value, request['name'])
            elif operation == 'call':
                result = value(*decode(request['args']), **{k: decode(v) for k, v in request['kwargs'].items()})
            elif operation == 'iterate':
                result = list(value)
            elif operation == 'length':
                result = len(value)
            elif operation == 'instance':
                result = isinstance(decode(request['value']), value)
            else:
                raise ValueError('Unsupported local KiCad operation')
            response = {'result': encode(result)}
        except Exception as exc:
            response = {'error': f'{type(exc).__name__}: {exc}'}
        print(json.dumps(response, ensure_ascii=True), flush=True)


class Remote:
    def __init__(self, connection, identity):
        self._connection, self._identity = connection, identity

    def __getattr__(self, name):
        return self._connection.request(self._identity, 'get', name=name)

    def __call__(self, *args, **kwargs):
        return self._connection.request(self._identity, 'call', args=args, kwargs=kwargs)

    def __iter__(self):
        return iter(self._connection.request(self._identity, 'iterate'))

    def __len__(self):
        return self._connection.request(self._identity, 'length')

    def __bool__(self):
        return True

    def __instancecheck__(self, instance):
        return self._connection.request(self._identity, 'instance', value=instance)


class Connection:
    def __init__(self, executable):
        self.process = subprocess.Popen([executable, str(Path(__file__).resolve()), '--serve'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, encoding='utf-8')
        atexit.register(self.close)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=5)

    def encode(self, value):
        if isinstance(value, Remote):
            return {'object': value._identity}
        if isinstance(value, (list, tuple)):
            return [self.encode(item) for item in value]
        if isinstance(value, dict):
            return {key: self.encode(item) for key, item in value.items()}
        return value

    def decode(self, value):
        if isinstance(value, dict) and 'object' in value:
            return Remote(self, value['object'])
        if isinstance(value, list):
            return [self.decode(item) for item in value]
        return value

    def request(self, identity, operation, **arguments):
        message = {'object': identity, 'operation': operation, **self.encode(arguments)}
        self.process.stdin.write(json.dumps(message) + '\n')
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError(f'KiCad subprocess terminated ({self.process.poll()})')
        response = json.loads(line)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return self.decode(response['result'])


if __name__ == '__main__':
    if sys.argv[1:] != ['--serve']:
        raise SystemExit('Internal local KiCad bridge')
    serve()
else:
    executable = os.environ.get('CARBENTRA_KICAD_PYTHON')
    if os.name == 'nt' and executable and Path(executable).resolve() != Path(sys.executable).resolve():
        pcbnew = Remote(Connection(executable), 0)
    else:
        pcbnew = importlib.import_module('pcbnew')
