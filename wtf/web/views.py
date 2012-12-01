import shutil
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

from pyes.query import FieldQuery, FieldParameter

from wtf.dates import format_es_date
from wtf.gravatar import gravatar_image_url
import wtf
from wtf.processing import (
    get_img_size,
    get_original_path,
    get_warped_img_path,
    save_normalized,
    warp_img,
)

import logging
log = logging.getLogger(__name__)


TOPDIR = os.path.dirname(wtf.__file__)
MEDIADIR = os.path.join(TOPDIR, 'media')
TMPLDIR = os.path.join(TOPDIR, 'templates')
TMPLS = TemplateLookup(directories=[TMPLDIR])
JOBTIMEOUT = 3600    # one hour
DOCDIR = os.path.join(TOPDIR, 'docs', 'build', 'html')


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
        request.response.set_cookie('browserid_csrf_token', csrf_token)

    if existing is None:
        return basic

    existing.update(basic)
    return existing


@view_config(route_name='index', request_method='GET', renderer='index.mako')
def index(request):
    """Index page."""
    return _basic(request)


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


@view_config(route_name='about_index')
def about_index(request):
    """Redirects / to /index.html"""
    return HTTPFound('/about/index.html')


@view_config(route_name='about_file')
def about_dir(request):
    """Returns Sphinx files"""
    filename = request.matchdict['file']
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    path = os.path.join(DOCDIR, filename)
    return FileResponse(path, request)


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
            log.error("Signup failure")
            log.error(res)
            raise HTTPServerError()

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
        base = _toint(request.POST['bottom_x']), _toint(request.POST['bottom_y'])
        top = _toint(request.POST['top_x']), _toint(request.POST['top_y'])
        warped_image, new_base, new_top = warp_img(orig_img, base, top)
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
    """Profile page."""
    if request.user is None:
        raise Forbidden()

    if 'picture' in request.POST:
        pic = request.POST['picture'].file
        ext = os.path.splitext(request.POST['picture'].filename)[-1]
        settings = dict(request.registry.settings)
        pic_dir = settings['thumbs.document_root']
        basename = str(uuid4())
        filename = os.path.join(pic_dir, basename + ext)

        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)

        save_normalized(pic, filename)

        pic.close()

        # Add to Elastic Search
        doc = {
            'user': request.user.id,
            'timestamp': datetime.datetime.utcnow(),
            'filename': filename,'gravatar': gravatar_image_url,
        }
        res = request.elasticsearch.index(doc, 'snaps', 'snaptype')
        if not res['ok']:
            log.error("Error while saving snap")
            log.error(res)
            raise HTTPServerError()

        request.session.flash('Image uploaded')
        return HTTPFound(location='/snapshot/%s' % basename + ext)

    return _basic(request)

