import os
import datetime
from uuid import uuid4

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPServerError,
)
from pyramid.response import FileResponse
from pyramid.security import authenticated_userid, forget
from pyramid.exceptions import Forbidden

from mako.lookup import TemplateLookup

from pyes.query import FieldQuery, FieldParameter, StringQuery

from wtf.dates import format_es_date
from wtf.gravatar import gravatar_image_url
import wtf
from wtf.processing import (
    get_img_size,
    get_original_path,
    save_normalized,
    warp_img,
)
from wtf import logger


TOPDIR = os.path.dirname(wtf.__file__)
MEDIADIR = os.path.join(TOPDIR, 'media')
TMPLDIR = os.path.join(TOPDIR, 'templates')
TMPLS = TemplateLookup(directories=[TMPLDIR])
JOBTIMEOUT = 3600    # one hour
DOCDIR = os.path.join(TOPDIR, 'docs', 'build', 'html')

# In memory feature cache to spare some CPU
FEATURES_CACHE = {}


def time2str(data):
    if data is None:
        return 'Unknown date'
    return datetime.datetime.fromtimestamp(data).strftime('%Y-%m-%d %H:%M:%S')


def _basic(request, existing=None):
    csrf_token = os.urandom(16).encode("hex")

    basic = {'messages': request.session.pop_flash(),
             'user': request.user,
             'gravatar': gravatar_image_url,
             'csrf_token': csrf_token,
             'came_from': request.path_qs}

    if not request.user:
        # set up the cookie
        request.response.set_cookie('browserid_csrf_token', csrf_token,
                                    path='/login')

    if existing is None:
        return basic

    existing.update(basic)
    return existing


@view_config(route_name='about', request_method='GET',
             renderer='about.mako')
def about(request):
    """About page."""
    return _basic(request)


@view_config(route_name='plants', request_method='GET',
             renderer='plants.mako')
def plants(request):
    """Plants page."""
    query = StringQuery('*')
    snaps = request.elasticsearch.search(query, size=10, indices=['plants'],
                                         )
    data = {'plants': snaps,
            'basename': os.path.basename,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='plant', request_method='GET',
             renderer='plant.mako')
def plant(request):
    """Plant page."""
    name = request.matchdict['file']
    query = FieldQuery(FieldParameter('plant', name))
    snaps = request.elasticsearch.search(query, size=10, indices=['snaps'])

    query = FieldQuery(FieldParameter('name', name))
    plant = list(request.elasticsearch.search(query, indices=['plants']))[0]

    filename = plant.get('filename')
    if filename:
        image = '/thumbs/large/' + os.path.basename(filename)
    else:
        image = '/media/tree_icon.png'

    data = {'name': name,
            'image': image,
            'snaps': snaps,
            'basename': os.path.basename,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='index', request_method='GET', renderer='index.mako')
def index(request):
    """Index page."""
    query = StringQuery('*')
    snaps = request.elasticsearch.search(query, size=10, indices=['snaps'])

    data = {'snaps': snaps,
            'basename': os.path.basename,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='profile', request_method=('GET', 'POST'),
             renderer='profile.mako')
def profile(request):
    """Profile page."""
    if request.user:
        query = FieldQuery(FieldParameter('user', request.user.id))
        snaps = request.elasticsearch.search(query, indices=['snaps'])
    else:
        snaps = []

    data = {'snaps': snaps,
            'basename': os.path.basename,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='sign')
def sign(request):
    """Initiates a Browser-ID challenge."""
    email = authenticated_userid(request)
    if email is None:
        raise Forbidden()

    # Signup new user
    query = FieldQuery(FieldParameter('email', email))
    res = request.elasticsearch.search(query)
    if len(res) == 0:
        doc = {
            'id': str(uuid4()),
            'email': email,
            'registered': datetime.datetime.utcnow(),
        }
        res = request.elasticsearch.index(doc, 'users', 'usertype')
        if res['ok'] == False:
            logger.error("Signup failure")
            logger.error(res)
            raise HTTPServerError()
        request.elasticsearch.refresh()

    return HTTPFound(location='/')


@view_config(route_name='logout')
def logout(request):
    """Logs out."""
    headers = forget(request)
    request.session.flash("Logged out")
    return HTTPFound(location='/', headers=headers)


def _toint(value):
    return int(float(value))


@view_config(route_name='snapshot', request_method=('GET', 'POST'),
             renderer='snapshot.mako')
def snapshot(request):
    """Index page."""
    filename = request.matchdict['file']
    settings = dict(request.registry.settings)
    pic_dir = settings['thumbs.document_root']
    orig_img = os.path.join(pic_dir, filename)

    height, width = get_img_size(orig_img)

    # security loop
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    if request.method == 'POST':
        base = _toint(request.POST['bottom_y']), _toint(request.POST['bottom_x'])
        top = _toint(request.POST['top_y']), _toint(request.POST['top_x'])
        query = FieldQuery(FieldParameter('filename', filename))
        warped_image, new_base, new_top = warp_img(orig_img, base, top)
        # There should be only one
        snap_idx = 'snaps'
        snaps = request.elasticsearch.search(query, size=2, indices=[snap_idx])
        if len(snaps) > 1:
            logger.warning("Found more than one snapshot for file %s", filename)
        elif len(snaps) >= 1:
            snap = snaps[0]
            snap['warped_filename'] = warped_image
            snap['warped'] = True
            snap['base_x'] = base[0]
            snap['base_y'] = base[1]
            snap['top_x'] = top[0]
            snap['top_y'] = top[1]
            request.elasticsearch.index(snap, snap_idx, 'snaptype')
            request.elasticsearch.refresh()
            # TODO: compute features here
            FEATURES_CACHE[warped_image] = 'FEATURES'
        return HTTPFound(location='/warped/%s' %
                os.path.basename(warped_image))

    data = {'snapshot': filename,
            'width': width,
            'height': height}

    return _basic(request, data)


@view_config(route_name='warped', request_method='GET',
             renderer='warped.mako')
def warped(request):
    """Index page."""
    filename = request.matchdict['file']
    settings = dict(request.registry.settings)
    pic_dir = settings['thumbs.document_root']
    orig_img = os.path.join(pic_dir, filename)
    res = get_img_size(orig_img)

    if len(res) == 2:
        height, width = res
    else:
        height, width = 500, 500

    # security loop
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    data = {'snapshot': filename,
            'original': get_original_path(filename),
            'width': width,
            'height': height}

    return _basic(request, data)


@view_config(route_name='picture')
def picture(request):
    settings = dict(request.registry.settings)
    pic_dir = settings['thumbs.document_root']

    filename = request.matchdict['file']
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    path = os.path.join(pic_dir, filename)
    return FileResponse(path, request)


@view_config(route_name='upload', request_method=('GET', 'POST'),
             renderer='upload.mako')
def upload(request):
    return _upload(request, 'snaps', 'snaptype', 'snapshot')


@view_config(route_name='upload_plant', request_method=('GET', 'POST'),
             renderer='upload_plant.mako')
def upload_plant(request):
    index, type_, root = 'plants', 'planttype', 'plant'
    ext = ''

    if request.user is None:
        raise Forbidden()

    if request.method == 'POST':
        pic = request.POST.get('picture')
        basename = request.POST.get('name', str(uuid4()))

        if pic not in (None, ''):
            filename, __ = _save_pic(pic, request, basename)
        else:
            filename = None

        # Add to Elastic Search
        doc = {
            'user': request.user.id,
            'timestamp': datetime.datetime.utcnow(),
            'filename': filename,
            'gravatar': gravatar_image_url(request.user.email),
            'geo_longitude': request.POST.get('longitude'),
            'geo_latitude': request.POST.get('latitude'),
            'geo_accuracy': request.POST.get('accuracy'),
            'name': request.POST.get('name')
        }

        res = request.elasticsearch.index(doc, index, type_)
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()

        request.elasticsearch.refresh()
        request.session.flash('Image uploaded')
        return HTTPFound(location='/%s/%s' % (root, basename + ext))

    return _basic(request)

@view_config(route_name='upload_plant_snaps', request_method='POST')
def upload_plant_snaps(request):
    plantname = request.POST['name']
    uploaded = 0
    for name, value in request.POST.items():
        if name == 'name':
            continue

        filename, ext = _save_pic(value, request)
        doc = {
	   'user': request.user.id,
           'timestamp': datetime.datetime.utcnow(),
           'filename': filename,
           'plant': plantname
        }
        res = request.elasticsearch.index(doc, 'snaps', 'snaptype')
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()

        uploaded +=1

    request.elasticsearch.refresh()
    request.session.flash("Uploaded %d snaps" % uploaded)
    return HTTPFound(location='/plant/%s' % plantname)


def _save_pic(fileupload, request, basename=None):
    if basename is None:
        basename = str(uuid4())
    pic = fileupload.file
    ext = os.path.splitext(fileupload.filename)[-1]
    settings = dict(request.registry.settings)
    pic_dir = settings['thumbs.document_root']
    filename = os.path.join(pic_dir, basename + ext)
    if not os.path.exists(pic_dir):
	os.makedirs(pic_dir)
    save_normalized(pic, filename)
    pic.close()
    return filename, ext


def _upload(request, index, type_, root):
    if request.user is None:
        raise Forbidden()

    if request.method == 'POST':
        pic = request.POST.get('picture')
        basename = request.POST.get('name', str(uuid4()))

        if pic is not None:
            filename, ext = _save_pic(pic, request, basename)
        else:
            filename = None
            ext = ''

        # Add to Elastic Search
        doc = {
            'user': request.user.id,
            'timestamp': datetime.datetime.utcnow(),
            'filename': filename,
            'gravatar': gravatar_image_url(request.user.email),
            'geo_longitude': request.POST.get('longitude'),
            'geo_latitude': request.POST.get('latitude'),
            'geo_accuracy': request.POST.get('accuracy'),
            'name': request.POST.get('name')
        }

        res = request.elasticsearch.index(doc, index, type_)
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()

        request.elasticsearch.refresh()
        request.session.flash('Image uploaded')
        return HTTPFound(location='/%s/%s' % (root, basename + ext))

    return _basic(request)
