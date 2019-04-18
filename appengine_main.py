from google.appengine.ext.webapp.template import render
from google.appengine.ext import ndb
from google.appengine.api import users, memcache
from googleapiclient.errors import HttpError
from urlparse import urlparse
import webapp2
import config
import gsuite


class Link(ndb.Model):
  url = ndb.StringProperty()
  owner_id = ndb.StringProperty()
  owner_name = ndb.StringProperty()
  viewcount = ndb.IntegerProperty()
  public = ndb.BooleanProperty()
  visibility = ndb.TextProperty()


def errorPage(response, code, message):
  context = {'code': code, 'message': message, 'corpname': config.CORP_NAME}
  response.write(render('template/error.html', context))
  response.set_status(code)


def isValidUrl(url):
  o = urlparse(url)
  if o.scheme in config.URL_ALLOWED_SCHEMAS:
    return 1
  return 0


class ShowLinks(webapp2.RequestHandler):

  def get(self, param):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.path))
      return
    sign_out_link = users.create_logout_url('/')
    is_admin = users.is_current_user_admin()
    if param == "all" and is_admin:
      links = Link.query().fetch()
    else:
      links = Link.query(Link.owner_id == user.user_id()).fetch()
    context = {
        "links": links,
        "is_admin": is_admin,
        "sign_out_link": sign_out_link,
        "fqdn": config.GOLINKS_FQDN,
        "hostname": config.GOLINKS_HOSTNAME
    }
    self.response.write(render("template/list.html", context))


class DeleteLink(webapp2.RequestHandler):

  def get(self, link):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.path))
      return
    key = link.rstrip("/")
    l = Link.get_by_id(key)
    if l.owner_id:
      if l.owner_id != user.user_id() and not users.is_current_user_admin():
        errorPage(self.response, 403, "Access denied")
        return
    l.key.delete()
    self.redirect("/links/my")


class EditLink(webapp2.RequestHandler):

  def post(self, link):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.path))
      return
    key = self.request.get("key", "").rstrip("/")
    url = self.request.get("url", None)
    public = self.request.get("public", 0)
    visibility = self.request.get("visibility", "")
    if not key:
      errorPage(self.response, 400, "Shortened URL required")
      return
    blacklist = ["edit", "links", "delete"]
    for word in blacklist:
      if key.startswith(word + '/') or key == word:
        errorPage(self.response, 400, "Shortened URL forbidden")
        return
    if link:
      if key != link:
        errorPage(self.response, 400, "Cannot change shortened URL")
        return
    if not isValidUrl(url):
      errorPage(self.response, 400, "URL Illegal")
      return
    l = Link.get_or_insert(key)
    if l.owner_id:
      if not link:
        errorPage(
            self.response, 500,
            "Link already exists... Please update existing one or change url.")
        return
      if l.owner_id != user.user_id() and not users.is_current_user_admin():
        errorPage(self.response, 403, "Access denied")
        return
    else:
      l.owner_id = user.user_id()
      l.owner_name = user.nickname()
    if config.ENABLE_GOOGLE_GROUPS_INTEGRATION:
      groups = map(lambda x: x.strip(), visibility.split(';'))
      for group in groups:
        if group:
          try:
            gsuite.directory_service.groups().get(groupKey=group).execute()
          except HttpError:
            errorPage(self.response, 400, "Invalid group: " + group)
            return
      l.visibility = visibility
    l.url = url
    if public:
      l.public = True
    else:
      l.public = False
    if not l.viewcount:
      l.viewcount = 0
    l.put()
    self.redirect("/edit/" + key)

  def get(self, link):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.path))
      return
    sign_out_link = users.create_logout_url('/')
    is_admin = users.is_current_user_admin()
    context = {
        "sign_out_link": sign_out_link,
        "is_admin": is_admin,
        "show_visibility": config.ENABLE_GOOGLE_GROUPS_INTEGRATION,
        'hostname': config.GOLINKS_HOSTNAME
    }
    if link:
      link = link.rstrip("/")
      context.update({'key': link})
      l = Link.get_by_id(link)
      if l:
        if l.owner_id:
          if l.owner_id != user.user_id() and not is_admin:
            errorPage(self.response, 403, "Access denied")
            return
        context.update({
            'url': l.url,
            'viewcount': l.viewcount,
            'public': l.public,
            'visibility': l.visibility or '',
            'can_delete': 1,
            'owner': l.owner_name
        })
    self.response.write(render("template/edit.html", context))


class RedirectLink(webapp2.RequestHandler):

  def get(self, link):
    user = users.get_current_user()
    if link:
      l = Link.get_by_id(link.rstrip("/"))
      if l:
        if not l.public:
          if not user:
            self.redirect(users.create_login_url(self.request.path))
            return
          if l.visibility:
            if config.ENABLE_GOOGLE_GROUPS_INTEGRATION:
              memcacheKey = "v_%s_%s" % (user.user_id(), link)
              if not config.USE_MEMCACHE or not memcache.get(memcacheKey):
                groups = map(lambda x: x.strip(), l.visibility.split(';'))
                no_access = True
                for group in groups:
                  if group:
                    try:
                      # NOTES: this does support nested group members but doesn't support external users
                      # even though we don't currently allow external users to log in, but this is worth noting if we decide to support
                      # See b/109861216 and https://github.com/googleapis/google-api-go-client/issues/350
                      if gsuite.directory_service.members().hasMember(
                          groupKey=group,
                          memberKey=user.email()).execute()['isMember']:
                        no_access = False
                        break
                    except HttpError:
                      pass
                if no_access:
                  # no caching for 403 so that user can gain access immediately
                  errorPage(self.response, 403,
                            "You do not have access to the requested resource")
                  return
              if config.USE_MEMCACHE:
                memcache.set(memcacheKey, 1, config.MEMCACHE_TTL)
        l.viewcount += 1
        l.put()
        self.redirect(str(l.url))
        return
    if not user:  # we don't want external to know if url exists
      self.redirect(users.create_login_url(self.request.path))
      return
    if not link:
      self.redirect('/links/my')
      return
    errorPage(self.response, 404, "Not Found!")


app = webapp2.WSGIApplication([
    ('/edit/([-\/\w]*)', EditLink),
    ('/delete/([-\/\w]+)', DeleteLink),
    ('/links/(\w*)', ShowLinks),
    ('/([-\/\w]*)', RedirectLink),
],
                              debug=True)
