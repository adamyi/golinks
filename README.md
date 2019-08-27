# go/ links
Just another Google-like go/ short-link service, deployed on GCP and integrated with G Suite!

## Background
While volunteering at Google Beijing, I learned that Google has an internal URL shortener
that allows users to register URL shortcuts for lengthy URLs. For example, if you are
interested in the first release preview of Flutter, you only need to visit
http://go/flutter-rp1. You want to see the blog post about it? Sure, just visit
http://go/flutter-rp1-blog! Those links can even be easily printed out on paper, and also
easily remembered. Life is a lot easier with those links.

According to [Kelly Norton](https://github.com/kellegous/go/blob/master/README.md), this
was originally implemented at Google by [Benjamin Staffin](https://www.linkedin.com/in/benjaminstaffin)
to end the never-ending stream of requests for internal CNAME entries. He described it as
AOL keywords for the corporate network.

Many companies now have something similar, and there's even a "go/ link as a service":
[golinks.io](https://golinks.io). This is my personal implementation, originally designed
for [MUNPANEL](https://munpanel.com), a student project of mine.

## Stack
It's built on top of [Google App Engine](https://cloud.google.com/appengine/), and
[Google Cloud Datastore](https://cloud.google.com/datastore/), so it scales really well,
and is really easy to deploy. It's written in Python 2.7, and I haven't tested support for
Python 3, but feel free to send a pull request if changes are needed to support Python 3.
It calls Google's OAuth API so it can integrate with your [G Suite](https://gsuite.google.com)
for SSO (Single-Sign On) and access control. For more advanced access control, it integrates
with [Google Groups](https://groups.google.com). It also has a pretty (imo) UI built with
[Material Design Lite](https://getmdl.io).

## Why another one?

As mentioned before, there are `go link as a service` platforms but it's not customizable enough
to suit individual needs and they are expensive to use. Security is another concern since it's
closed-source and hosted by third-party.

Kelly Norton wrote a decent [one](https://github.com/kellegous/go) in Golang, but it needs
to be deployed in a container/VM. It also lacks advanced features and doesn't support any sort
of Access Control.

So I decided to write my own. It's deployed on
[Google App Engine](https://cloud.google.com/appengine/) so it's much easier to maintain and scale.
It integrates directly with [G Suite](https://gsuite.google.com). It also integrates with
[Google Groups](https://groups.google.com) for more advanced access control.

## Usage
You can easily log in to your G Suite account, view the links you created, create new links,
modify links, delete links, and see how many times your links have been clicked, all on the
web portal.

For every link, you can specify whether it requires G Suite login. You can also specify
if it requires G Suite user to belong to certain Google Groups to access that specific URL.

## Deploy
1. Create a new GCP project.
2. `pip install -t lib -r requirements.txt`
3. Copy `config.py.example` to `config.py` and modify accordingly
4. `gcloud app deploy app.yaml`
5. Go to GCP app engine settings, set `Google authentication` to `Google Apps domain` for
G Suite integration
6. In App Engine settings, configure your custom domain (e.g. go.corp.munpanel.com)
7. Visit the domain you just set, and enjoy :-)

## Google Groups Integration
We support integration with Google Groups for more advanced access control on top of 
regular G Suite integration. For each link, you can specify users in which internal Google 
Group have access.

To set up Google Groups Integration, follow the following steps:
1. Turn on `ENABLE_GOOGLE_GROUPS_INTEGRATION` in `config.py` and set `GSUITE_DIRECTORY_ADMIN_USER`
to a G Suite admin user in your domain.
2. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) settings for your
GCP project and create a new service account (you don't need to grant any GCP project or user access to
the service account); enable `G Suite Domain-wide Delegation` for it. Download json format
key and put it as `credentials.json` in your GAE project root.
3. Go to [G Suite Admin](https://admin.google.com), select `Security`, `Advanced Setttings`,
`Manage API Access`
4. Authorize a new access, set `Client Name` to the `Client ID` under `G Suite Domain-wide
Delegation`, set scope to
`https://www.googleapis.com/auth/admin.directory.group.readonly, https://www.googleapis.com/auth/admin.directory.group.member.readonly `
5. Go to [GCP API Library](https://console.cloud.google.com/apis/api/admin.googleapis.com/overview) and enable
`Admin SDK` API for your GCP project.

## Contributing
Contribution is welcome! Feel free to send pull requests ^_^

## License
[MIT License](LICENSE)

## Author
[Adam Yi](https://github.com/adamyi)

## Disclaimer
This product is neither endorsed nor supported by Google LLC.
