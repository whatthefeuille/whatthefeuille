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
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='plant', request_method='GET',
             renderer='plant.mako')
def plant(request):
    """Plant page."""
    filename = request.matchdict['file']
    name = os.path.basename(filename)
    query = FieldQuery(FieldParameter('plant', name))
    snaps = request.elasticsearch.search(query, size=10, indices=['snaps'])

    # TODO: we should use plant id here instead
    query = FieldQuery(FieldParameter('name', name))
    plant = list(request.elasticsearch.search(query, indices=['plants']))[0]

    filename = plant.get('filename')
    if filename:
        image = '/thumbs/large/' + filename
    else:
        image = '/media/tree_icon.png'

    data = {'name': name,
            'image': image,
            'snaps': snaps,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='index', request_method='GET', renderer='index.mako')
def index(request):
    """Index page."""
    query = StringQuery('*')
    snaps = request.elasticsearch.search(query, size=10, indices=['snaps'])

    data = {'snaps': snaps,
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
        res = request.elasticsearch.index(doc, 'users', 'usertype', doc['id'])
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
    file_path = os.path.join(pic_dir, filename)

    height, width = get_img_size(file_path)

    # security loop
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    file_uuid = os.path.splitext(filename)[0]

    if request.method == 'POST':
        base = _toint(request.POST['bottom_y']), _toint(request.POST['bottom_x'])
        top = _toint(request.POST['top_y']), _toint(request.POST['top_x'])
        warped_img_path, new_base, new_top = warp_img(file_path, base, top)
        # There should be only one
        snap_idx, snap_type = 'snaps', 'snaptype'
        snap = request.elasticsearch.get(snap_idx, snap_type, file_uuid)
        warped_filename = os.path.basename(warped_img_path)
        if snap is not None:
            snap['warped_filename'] = warped_filename
            snap['warped'] = True
            snap['base_x'] = base[0]
            snap['base_y'] = base[1]
            snap['top_x'] = top[0]
            snap['top_y'] = top[1]
            logger.debug("Updating snap %s: %r", file_uuid, snap)
            request.elasticsearch.index(snap, snap_idx, snap_type, file_uuid)
            request.elasticsearch.refresh()
            # TODO: compute features here
            FEATURES_CACHE[warped_filename] = 'FEATURES'
        else:
            logger.warning("Could not find snap for %s", file_uuid)
        return HTTPFound(location='/warped/%s' % warped_filename)

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

    if request.user is None:
        raise Forbidden()

    if request.method == 'POST':
        pic = request.POST.get('picture')
        name = request.POST.get('name', str(uuid4()))

        if pic not in (None, ''):
            name, ext = _save_pic(pic, request, name)
            filename = name, ext
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
            'name': name,
        }
        res = request.elasticsearch.index(doc, index, type_, name)
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()
        request.elasticsearch.refresh()
        request.session.flash('Plant registered')
        return HTTPFound(location='/%s/%s' % (root, name))

    return _basic(request)

@view_config(route_name='upload_plant_snaps', request_method='POST')
def upload_plant_snaps(request):
    plant_name = request.POST['name']
    uploaded = 0
    for name, value in request.POST.items():
        if name == 'name':
            continue
        if value == u'':
            continue
        logger.debug('Saving snap %r for plant %s', value, plant_name)
        file_uuid, ext = _save_pic(value, request)
        doc = {
           'user': request.user.id,
           'timestamp': datetime.datetime.utcnow(),
           'filename': file_uuid + ext,
           'plant': plant_name,
        }
        res = request.elasticsearch.index(doc, 'snaps', 'snaptype', file_uuid)
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()
        uploaded += 1

    request.elasticsearch.refresh()
    request.session.flash("Uploaded %d snaps" % uploaded)
    return HTTPFound(location='/plant/%s' % plant_name)


def _save_pic(fileupload, request, file_uuid=None):
    if file_uuid is None:
        file_uuid = str(uuid4())
    pic = fileupload.file
    ext = os.path.splitext(fileupload.filename)[-1]
    settings = dict(request.registry.settings)
    pic_dir = settings['thumbs.document_root']
    filepath = os.path.join(pic_dir, file_uuid + ext)
    if not os.path.exists(pic_dir):
        os.makedirs(pic_dir)
    save_normalized(pic, filepath)
    pic.close()
    return file_uuid, ext


def _upload(request, index, type_, root):
    if request.user is None:
        raise Forbidden()

    if request.method == 'POST':
        pic = request.POST.get('picture')
        file_uuid = request.POST.get('name', str(uuid4()))
        if pic is not None:
            file_uuid, ext = _save_pic(pic, request, file_uuid)
        else:
            ext = '.bin'

        # Add to Elastic Search
        doc = {
            'user': request.user.id,
            'timestamp': datetime.datetime.utcnow(),
            'filename': file_uuid + ext,
            'gravatar': gravatar_image_url(request.user.email),
            'geo_longitude': request.POST.get('longitude'),
            'geo_latitude': request.POST.get('latitude'),
            'geo_accuracy': request.POST.get('accuracy'),
            'name': request.POST.get('name')
        }

        res = request.elasticsearch.index(doc, index, type_, file_uuid)
        if not res['ok']:
            logger.error("Error while saving index %r for %r",
                         index, file_uuid)
            logger.error(res)
            raise HTTPServerError()

        request.elasticsearch.refresh()
        request.session.flash('Image uploaded')
        return HTTPFound(location='/%s/%s' % (root, file_uuid + ext))

    return _basic(request)
