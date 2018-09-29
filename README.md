# go/ links
Just another Google-like go/ links service, deployed on GCP and integrated with G Suite!

## Background
While volunteering at Google Beijing, I learned that Google has an internal URL shortener
that allows users to register URL shortcuts for lengthy URLs. For example, if you are
interested in the first release preview of Flutter, you only need to visit
http://go/flutter-rp1. You want to see the blog post about it? Sure, just visit
http://go/flutter-rp1-blog! Those links can even be easily printed out on paper, and also
easily remembered. Life is simply so great with those links.

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
for SSO (Single-Sign On) and access control. It also has a pretty (imo) UI built with
[Material Design Lite](https://getmdl.io).

## Deploy
1. Create a new GCP project.
2. `gcloud app deploy app.yaml`
3. Go to GCP app engine settings, set `Google authentication` to `Google Apps domain` for
G Suite integration
4. In App Engine settings, configure your custom domain (e.g. go.corp.munpanel.com)
5. Visit the domain you just set, and enjoy :-)

## Usage
You can easily log in to your G Suite account, view the links you created, create new links,
modify links, delete links, and see how many times your links have been clicked, all on the
web portal.

## Contributing
Contribution is welcome! Feel free to send pull requests ^_^

## License
[MIT License](LICENSE)

## Author
[Adam Yi](https://github.com/adamyi)

## Disclaimer
This product is neither endorsed nor supported by Google LLC.
