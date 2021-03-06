import os
import datetime
from uuid import uuid4
from collections import OrderedDict

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPServerError,
)
from pyramid.response import FileResponse
from pyramid.security import forget
from pyramid.exceptions import Forbidden

from mako.lookup import TemplateLookup

from pyes.query import FieldQuery, FieldParameter, StringQuery
from pyes.exceptions import NotFoundException

from wtf.dates import format_es_date
from wtf.gravatar import gravatar_image_url
import wtf
from wtf.processing import (
    get_img_size,
    get_original_path,
    save_normalized,
    warp_img,
    compute_features_collection,
    suggest_snaps,
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
    snaps = request.db.search(query, size=10, indices=['plants'],
                              sort='name')
    data = {'plants': snaps,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='plant', request_method='GET',
             renderer='plant.mako')
def plant(request):
    """Plant page."""
    name = request.matchdict['name']
    query = FieldQuery(FieldParameter('plant', name))
    snaps = request.db.search(query, size=20, indices=['snaps'],
                              sort='timestamp:desc')

    # TODO: we should use plant id here instead
    query = FieldQuery(FieldParameter('name', name))
    plants = list(request.db.search(query, indices=['plants']))
    if not plants:
        raise HTTPNotFound("No plant registered under %s" % name)
    plant = plants[0]
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
    snaps = request.db.search(query, size=10, indices=['snaps'],
                              sort='timestamp:desc')

    data = {'snaps': snaps,
            'format_date': format_es_date}

    return _basic(request, data)


@view_config(route_name='profile', request_method=('GET', 'POST'),
             renderer='profile.mako')
def profile(request):
    """Profile page."""
    if request.user:
        query = FieldQuery(FieldParameter('user', request.user.id))
        snaps = request.db.search(query, indices=['snaps'],
                                  sort='timestamp:desc')
    else:
        snaps = []

    data = {'snaps': snaps,
            'format_date': format_es_date}

    return _basic(request, data)


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

    try:
        height, width = get_img_size(file_path)
    except IOError:
        logger.error("Failed to open file with path: %s", file_path,
                     exc_info=True)
        raise HTTPNotFound("Could not load image for snap %s" % filename)

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
        snap = request.db.get(snap_idx, snap_type, file_uuid)
        warped_filename = os.path.basename(warped_img_path)
        if snap is not None:
            snap['warped_filename'] = warped_filename
            snap['warped'] = True
            snap['base_x'] = base[0]
            snap['base_y'] = base[1]
            snap['top_x'] = top[0]
            snap['top_y'] = top[1]
            logger.debug("Warping snap %s", file_uuid)
            request.db.index(snap, snap_idx, snap_type, file_uuid)
            request.db.refresh()
            # Precompute the cached features incrementally
            compute_features_collection([snap], pic_dir, cache=FEATURES_CACHE)
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

    warped_stemname = os.path.splitext(filename)[0]
    snap_idx, snap_type = 'snaps', 'snaptype'

    if warped_stemname.endswith('_warped'):
        file_uuid = warped_stemname[:-len('_warped')]
    else:
        logger.warning(
            'Warped stemname is expected to end with "_warped", got: %s',
            warped_stemname
        )
        file_uuid = warped_stemname

    try:
        current_snap = request.db.get(snap_idx, snap_type, file_uuid)
    except NotFoundException:
        raise HTTPNotFound("Could not find snapshot for %s" % file_uuid)

    next_snap = None
    unwarped_count = ""

    if not current_snap.plant:
        query = FieldQuery(FieldParameter('warped', True))
        candidates = request.db.search(query, size=200, indices=['snaps'],
                                       sort='timestamp:desc')

        # TODO: filter out non-plant snaps in the query directly
        candidates = [c for c in candidates if c.plant != None]

        logger.debug('Computing suggestion for %s', current_snap.filename)
        best_snaps, scores = suggest_snaps(current_snap, candidates, pic_dir,
                                           FEATURES_CACHE)
        suggestions = OrderedDict()
        for i, (snap, score) in enumerate(zip(best_snaps, scores)):
            name = snap.plant
            logger.debug("#%02d: %s with score = %f - %s",
                         i, name, score, snap.filename)
            suggestion = suggestions.get(name)
            if suggestion is None:
                query = FieldQuery(FieldParameter('name', name))
                plants = list(request.db.search(query, indices=['plants']))
                if not plants:
                    raise HTTPNotFound("No plant registered under %s"
                                       % name)
                plant = plants[0]
                suggestions[name] = (plant, [snap])
            else:
                suggestion[1].append(snap)
    else:
        suggestions = None

        # Suggest to warp the next unwarped snapshot from the same plant
        query = FieldQuery(fieldparameters=(
            FieldParameter('warped', None),
            FieldParameter('filename', '-' + current_snap.filename),
            FieldParameter('plant', current_snap.plant)))
        max_count = 100
        next_snaps = request.db.search({
            "bool" : {
                "must" : [
                    {'field': {'filename': '-' + current_snap.filename}},
                    {'field': {'plant': current_snap.plant}},
                ],
                "must_not" : [
                    {'field': {'warped': True}},
                ],
            },
        }, size=max_count, indices=['snaps'], sort='timestamp:desc')
        logger.debug(len(next_snaps))
        if len(next_snaps) > 0:
            next_snap = next_snaps[0]

        unwarped_count = "%d" % len(next_snaps)
        if len(next_snaps) == max_count:
            unwarped_count += "+"

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
            'height': height,
            'snap': current_snap,
            'uuid': file_uuid,
            'suggestions': suggestions,
            'next_snap': next_snap,
            'unwarped_count': unwarped_count}

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
        name = request.POST.get('name', '')
        if not name:
            name = str(uuid4())

        if pic not in (None, ''):
            name, ext = _save_pic(pic, request, name)
            filename = name + ext
        else:
            filename = None

        # TODO: check if plant exist first
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
        logger.debug("Indexing plant %s: %r", name, doc)
        res = request.db.index(doc, index, type_, name)
        if not res['ok']:
            logger.error("Error while creating plant %s", name)
            logger.error(res)
            raise HTTPServerError()
        request.db.refresh()
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
        res = request.db.index(doc, 'snaps', 'snaptype', file_uuid)
        if not res['ok']:
            logger.error("Error while saving index")
            logger.error(res)
            raise HTTPServerError()
        uploaded += 1

    request.db.refresh()
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

        res = request.db.index(doc, index, type_, file_uuid)
        if not res['ok']:
            logger.error("Error while saving index %r for %r",
                         index, file_uuid)
            logger.error(res)
            raise HTTPServerError()

        request.db.refresh()
        request.session.flash('Image uploaded')
        return HTTPFound(location='/%s/%s' % (root, file_uuid + ext))

    return _basic(request)


@view_config(route_name='pick', request_method='POST')
def pick(request):
    plant_name = request.POST['plant']
    leaf_uuid = request.POST['leaf'][:-len('_warped')]
    snap_idx, snap_type = 'snaps', 'snaptype'
    doc = request.db.get(snap_idx, snap_type, leaf_uuid)
    doc['plant'] = plant_name
    res = request.db.index(doc, snap_idx, snap_type, leaf_uuid)
    if not res['ok']:
        logger.error("Error while saving index")
        logger.error(res)
        raise HTTPServerError()

    request.db.refresh()
    request.session.flash("Picked %s!" % plant_name)
    base, ext = os.path.splitext(doc.filename)
    return HTTPFound(location='/warped/%s_warped%s' % (base, ext))
