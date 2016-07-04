# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to keep track of blocs such as examples, FAQ, ...

.. versionadded:: 1.4
"""
import sys
import os
from docutils import nodes
from docutils.parsers.rst import directives

import sphinx
from sphinx.locale import _
from sphinx.environment import NoUri
from sphinx.util.nodes import set_source_info
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.statemachine import StringList
from ..texthelper.texts_language import TITLES


class blocref_node(nodes.admonition):
    """
    defines ``blocref`` ndoe
    """
    pass


class blocreflist(nodes.General, nodes.Element):
    """
    defines ``blocreflist`` node
    """
    pass


class BlocRef(BaseAdmonition):
    """
    A ``blocref`` entry, displayed in the form of an admonition.
    It takes the following options:

    * title: a title for the bloc
    * tag: a tag to have several categories of blocs
    * lid: a label to refer to

    Example::

        .. blocref::
            :title: example of a blocref
            :tag: example
            :lid: id-you-can-choose

            An example of code::

                print("mignon")


    Which renders as:

    .. blocref::
        :title: example of a blocref
        :tag: dummy_example
        :lid: id-you-can-choose

        An example of code::

            print("mignon")

    All blocs can be displayed in another page by using ``blocreflist``::

        .. blocreflist::
            :tag: dummy_example
            :sort: title

    Only examples tagged as ``example`` will be inserted here.
    The option ``sort`` sorts items by *title*, *number*, *file*.
    You also link to it by typing ``:ref:'anchor <id-you-can-choose>' `` which gives
    something like :ref:`link_to_blocref <id-you-can-choose>`. The link must receive a name.

    .. blocreflist::
        :tag: dummy_example
        :sort: title
    """

    node_class = blocref_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class': directives.class_option,
        'title': directives.unchanged,
        'tag': directives.unchanged,
        'lid': directives.unchanged,
    }

    def run(self):
        """
        builds the blocref text
        """
        # sett = self.state.document.settings
        # language_code = sett.language_code
        lineno = self.lineno

        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        docname = None if env is None else env.docname
        if docname is None:
            docname = docname.replace("\\", "/").split("/")[-1]
            legend = "{0}:{1}".format(docname, lineno)
        else:
            legend = ''

        if not self.options.get('class'):
            self.options['class'] = ['admonition-blocref']

        # body
        (blocref,) = super(BlocRef, self).run()
        if isinstance(blocref, nodes.system_message):
            return [blocref]

        # add a label
        lid = self.options.get('lid', None)
        if lid:
            container = nodes.container()
            tnl = [".. _{0}:".format(lid), ""]
            content = StringList(tnl)
            self.state.nested_parse(content, self.content_offset, container)
        else:
            container = None

        # mid
        breftag = self.options.get('tag', '').strip()
        if len(breftag) == 0:
            raise ValueError("tag is empty")
        if env is not None:
            mid = int(env.new_serialno('indexbrefeu-%s' % breftag)) + 1
        else:
            mid = -1

        # title
        title = self.options.get('title', "").strip()
        if len(title) == 0:
            raise ValueError("title is empty")

        # main node
        ttitle = title
        title = nodes.title(text=_(title))
        if container is not None:
            blocref.insert(0, title)
            blocref.insert(0, container)
        else:
            blocref.insert(0, title)
        blocref['breftag'] = breftag
        blocref['brefmid'] = mid
        blocref['breftitle'] = ttitle
        blocref['brefline'] = lineno
        blocref['breffile'] = docname
        set_source_info(self, blocref)

        if env is not None:
            targetid = 'indexbrefe%s%s' % (
                breftag, env.new_serialno('indexbrefe%s' % breftag))
            ids = [targetid]
            targetnode = nodes.target(legend, legend, ids=ids)
            # self.state.add_target(ids[0], legend, '', targetnode, lineno)
            return [targetnode, blocref]
        else:
            return [blocref]


def process_blocrefs(app, doctree):
    """
    collect all blocrefs in the environment
    this is not done in the directive itself because it some transformations
    must have already been run, e.g. substitutions
    """
    env = app.builder.env
    if not hasattr(env, 'blocref_all_blocrefs'):
        env.blocref_all_blocrefs = []
    for node in doctree.traverse(blocref_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError
        except IndexError:
            targetnode = None
        newnode = node.deepcopy()
        breftag = newnode['breftag']
        breftitle = newnode['breftitle']
        brefmid = newnode['brefmid']
        brefline = newnode['brefline']
        breffile = newnode['breffile']
        del newnode['ids']
        del newnode['breftag']
        env.blocref_all_blocrefs.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'blocref': newnode,
            'target': targetnode,
            'breftag': breftag,
            'breftitle': breftitle,
            'brefmid': brefmid,
            'brefline': brefline,
            'breffile': breffile,
        })


class BlocRefList(Directive):
    """
    A list of all blocref entries, for a specific tag.

    * tag: a tag to have several categories of blocref

    Example::

        .. blocreflist::
            :tag: issue
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'tag': directives.unchanged,
        'sort': directives.unchanged,
    }

    def run(self):
        """
        Simply insert an empty blocreflist node which will be replaced later
        when process_blocref_nodes is called
        """
        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        tag = self.options.get('tag', '').strip()
        if env is not None:
            targetid = 'indexbrefelist-%s' % env.new_serialno('indexbrefelist')
            targetnode = nodes.target('', '', ids=[targetid])
            n = blocreflist('')
            n["breftag"] = tag
            n["brefsort"] = self.options.get('sort', '').strip()
            return [targetnode, n]
        else:
            n = blocreflist('')
            n["breftag"] = tag
            n["brefsort"] = self.options.get('sort', '').strip()
            return [n]


def process_blocref_nodes(app, doctree, fromdocname):
    """
    process_blocref_nodes
    """
    if not app.config['blocref_include_blocrefs']:
        for node in doctree.traverse(blocref_node):
            node.parent.remove(node)

    # Replace all blocreflist nodes with a list of the collected blocrefs.
    # Augment each blocref with a backlink to the original location.
    env = app.builder.env
    if hasattr(env, "settings") and hasattr(env.settings, "language_code"):
        lang = env.settings.language_code
    else:
        lang = "en"

    orig_entry = TITLES[lang]["original entry"]
    brefmes = TITLES[lang]["brefmes"]

    if not hasattr(env, 'blocref_all_blocrefs'):
        env.blocref_all_blocrefs = []

    for ilist, node in enumerate(doctree.traverse(blocreflist)):
        if 'ids' in node:
            node['ids'] = []
        if not app.config['blocref_include_blocrefs']:
            node.replace_self([])
            continue

        nbbref = 0
        content = []
        breftag = node["breftag"]
        brefsort = node["brefsort"]

        # sorting
        if brefsort == 'title':
            double_list = [(info.get('breftitle', ''), info)
                           for info in env.blocref_all_blocrefs]
            double_list.sort(key=lambda x: x[:1])
        elif brefsort == 'file':
            double_list = [((info.get('breffile', ''), info.get('brefline', '')), info)
                           for info in env.blocref_all_blocrefs]
            double_list.sort(key=lambda x: x[:1])
        elif brefsort == 'number':
            double_list = [(info.get('brefmid', ''), info)
                           for info in env.blocref_all_blocrefs]
            double_list.sort(key=lambda x: x[:1])
        else:
            raise ValueError("sort option should be file, number, title")

        # printing
        for n, blocref_info_ in enumerate(double_list):
            blocref_info = blocref_info_[1]
            if blocref_info["breftag"] != breftag:
                continue

            nbbref += 1
            para = nodes.paragraph(classes=['blocref-source'])
            if app.config['blocref_link_only']:
                description = _('<<%s>>' % orig_entry)
            else:
                description = (
                    _(brefmes) %
                    (orig_entry, os.path.split(blocref_info['source'])[-1],
                     blocref_info['lineno'])
                )
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>') + 2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis(
                _(orig_entry), _(orig_entry))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, blocref_info['docname'])
                newnode['refuri'] += '#' + blocref_info['target']['refid']
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the blocref content
            blocref_entry = blocref_info['blocref']
            blocref_entry["ids"] = ["index-blocref-%d-%d" % (ilist, n)]
            # it apparently requires an attributes ids

            env.resolve_references(blocref_entry, blocref_info['docname'],
                                   app.builder)

            # Insert into the blocreflist
            content.append(blocref_entry)
            content.append(para)

        node.replace_self(content)


def purge_blocrefs(app, env, docname):
    """
    purge_blocrefs
    """
    if not hasattr(env, 'blocref_all_blocrefs'):
        return
    env.blocref_all_blocrefs = [blocref for blocref in env.blocref_all_blocrefs
                                if blocref['docname'] != docname]


def merge_blocref(app, env, docnames, other):
    """
    merge_blocref
    """
    if not hasattr(other, 'blocref_all_blocrefs'):
        return
    if not hasattr(env, 'blocref_all_blocrefs'):
        env.blocref_all_blocrefs = []
    env.blocref_all_blocrefs.extend(other.blocref_all_blocrefs)


def visit_blocref_node(self, node):
    """
    visit_blocref_node
    """
    self.visit_admonition(node)


def depart_blocref_node(self, node):
    """
    depart_blocref_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def visit_blocreflist_node(self, node):
    """
    visit_blocreflist_node
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.visit_admonition(node)


def depart_blocreflist_node(self, node):
    """
    depart_blocref_node
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``blocref`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('blocref', blocref_node)
        app.add_mapping('blocreflist', blocreflist)

    app.add_config_value('blocref_include_blocrefs', False, 'html')
    app.add_config_value('blocref_link_only', False, 'html')

    app.add_node(blocreflist,
                 html=(visit_blocreflist_node, depart_blocreflist_node),
                 latex=(visit_blocreflist_node, depart_blocreflist_node),
                 text=(visit_blocreflist_node, depart_blocreflist_node),
                 man=(visit_blocreflist_node, depart_blocreflist_node),
                 texinfo=(visit_blocreflist_node, depart_blocreflist_node))
    app.add_node(blocref_node,
                 html=(visit_blocref_node, depart_blocref_node),
                 latex=(visit_blocref_node, depart_blocref_node),
                 text=(visit_blocref_node, depart_blocref_node),
                 man=(visit_blocref_node, depart_blocref_node),
                 texinfo=(visit_blocref_node, depart_blocref_node))

    app.add_directive('blocref', BlocRef)
    app.add_directive('blocreflist', BlocRefList)
    if sys.version_info[0] == 2:
        # Sphinx does not accept unicode here
        app.connect('doctree-read'.encode("ascii"), process_blocrefs)
        app.connect('doctree-resolved'.encode("ascii"), process_blocref_nodes)
        app.connect('env-purge-doc'.encode("ascii"), purge_blocrefs)
        app.connect('env-merge-info'.encode("ascii"), merge_blocref)
    else:
        app.connect('doctree-read', process_blocrefs)
        app.connect('doctree-resolved', process_blocref_nodes)
        app.connect('env-purge-doc', purge_blocrefs)
        app.connect('env-merge-info', merge_blocref)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}