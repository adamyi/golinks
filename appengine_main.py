from google.appengine.ext.webapp.template import render
from google.appengine.ext import ndb
from google.appengine.api import users
from urlparse import urlparse
import webapp2

class Link(ndb.Model):
    url = ndb.StringProperty()
    owner_id = ndb.StringProperty()
    owner_name = ndb.StringProperty()
    viewcount = ndb.IntegerProperty()
    public = ndb.BooleanProperty()

def errorPage(response, code, message):
    context = {
       'code': code,
       'message': message
    }
    response.write(render('template/error.html', context))
    response.set_status(code)

def isValidUrl(url):
    o = urlparse(url)
    if o.scheme in ['http', 'https', 'mailto', 'ftp']:
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
        context = { "links": links, "is_admin": is_admin, "sign_out_link": sign_out_link }
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
        if not key:
            errorPage(self.response, 400, "Shortened URL required")
            return
        if key.startswith("edit/") or key == "edit":
            errorPage(self.response, 400, "Shortened URL forbidden")
            return
        if link:
            if key != link:
                errorPage(self.response, 400, "Cannot change shortened URL")
                return
        if not isValidUrl(url):
            errorPage(self.response, 400, "URL Illegal")
        l = Link.get_or_insert(key)
        if l.owner_id:
            if not link:
                errorPage(self.response, 500, "Link already exists... Please update existing one or change url.")
                return
            if l.owner_id != user.user_id() and not users.is_current_user_admin():
                errorPage(self.response, 403, "Access denied")
                return
        else:
            l.owner_id = user.user_id()
            l.owner_name = user.nickname()
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
        context = { "sign_out_link": sign_out_link, "is_admin": is_admin }
        if link:
            link = link.rstrip("/")
            context = { "sign_out_link": sign_out_link, "key": link, "is_admin": is_admin }
            l = Link.get_by_id(link)
            if l:
                if l.owner_id:
                    if l.owner_id != user.user_id() and not is_admin:
                        errorPage(self.response, 403, "Access denied")
                        return
                context = { "sign_out_link": sign_out_link, "key": l.key.id(), "url": l.url, "viewcount": l.viewcount, "public": l.public, "can_delete": 1, "owner": l.owner_name, "is_admin": is_admin }
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
                l.viewcount += 1
                l.put()
                self.redirect(str(l.url))
                return
        if not user: # we don't want external to know if url exists
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
], debug=True)
