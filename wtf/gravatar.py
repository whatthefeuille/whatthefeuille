from hashlib import md5


def gravatar_image_url(email, size=None):
    hsh = md5()
    hsh.update(email.strip().lower())
    url = "http://www.gravatar.com/avatar/%s" % hsh.hexdigest()
    if size:
        url += "?s=%d" % size
    return url
