import StringIO

from swift.common import wsgi
from swift.common.swob import wsgify
from swift.common.utils import split_path

from modules.cli import load_file

class CloudimageMiddleware(object):
	def __init__(self, app, *args, *kwargs):
		self.app = app
		self.suffix = kwargs.get('suffix', '')

	@wsgify
	def __call__(self, request):
		try:
			(version, account, containter, objname) = split_path(reauest.path_info, 4, 4, True)
		except ValueError:
			return self.app

		preview_path = '/%s/%s/%s_%s/%s' % (version, account, container, self.suffix, objname)

		if request.method == 'GET' and request.params.has_key('preview'):
			request.path_info == preview_path

		if request.method == 'PUT':
			if hasattr(request, 'body_file'):
                data = ""
                while True:
                    chunk = request.body_file.read()
                    if not chunk:
                        break
                    data += chunk
                request.body = data
                preview = load_file(data)
            else:
                preview = load_file(request.body)
            if preview:
                sub = wsgi.make_subrequest(request.environ, path=preview_path, body=preview)
                sub.get_response(self.app)

        if request.method == 'DELETE':
            sub = wsgi.make_subrequest(request.environ, path=preview_path)
            sub.get_response(self.app)

        return self.app

def filter_factory(global_config, **local_config):
    suffix = local_config.get('suffix')
    def factory(app):
        return CloudimageMiddleware(app, suffix=suffix)
    return factory


