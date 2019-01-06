"""Generate Sitemap XML."""

import os
import itertools
import textwrap
import gzip as _gzip

import jinja2
import schema

from ._misc import iterdocuments, parameters
from holocron.content import Document


_template = jinja2.Template(textwrap.dedent('''\
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {%- for doc in documents %}
      <url>
        <loc>{{ doc.abs_url | e }}</loc>
        <lastmod>{{ doc.updated.isoformat() | e }}</lastmod>
      </url>
    {% endfor -%}
    </urlset>
'''))


def _check_documents_urls(sitemap, documents):
    owned_url = os.path.dirname(sitemap.abs_url)

    for document in documents:
        if not document.abs_url.startswith(owned_url):
            raise ValueError(
                "The location of a Sitemap file determines the set of URLs "
                "that can be included in that Sitemap. A Sitemap file located "
                "at %s can include any URLs starting with %s but can not "
                "include %s." % (sitemap.abs_url, owned_url, document.abs_url))


@parameters(
    schema={
        'when': schema.Or([{str: object}], None, error='unsupported value'),
        'gzip': schema.Schema(bool),
        'save_as': schema.Schema(str),
    }
)
def process(app, documents, *, when=None, gzip=False, save_as='sitemap.xml'):
    passthrough, documents = itertools.tee(documents)
    selected, selected_check = itertools.tee(iterdocuments(documents, when))

    # According to the Sitemap protocol, the output encoding must be UTF-8.
    # Since this processor does not perform any I/O, the only thing we can
    # do here is to provide bytes representing UTF-8 encoded XML.
    content = _template.render(documents=selected)
    content = content.encode('UTF-8')

    # According to the Sitemap protocol, the sitemap.xml can be compressed
    # using gzip to reduce bandwidth requirements.
    if gzip:
        content = _gzip.compress(content)
        save_as += '.gz'

    sitemap = Document(app)
    sitemap['source'] = 'virtual://sitemap'
    sitemap['destination'] = save_as
    sitemap['content'] = content

    # According to the Sitemap protocol, the sitemap.xml location determines
    # the set of URLs that can be included in that sitemap. So we need to
    # check those before proceeding, and raise an exception if restriction
    # is broken.
    _check_documents_urls(sitemap, iterdocuments(selected_check, when))

    yield from passthrough
    yield sitemap
