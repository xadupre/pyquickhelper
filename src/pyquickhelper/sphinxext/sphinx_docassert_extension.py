# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension which if all parameters are documented.

.. versionadded:: 1.5
"""
from docutils import nodes
import inspect
import sphinx
from sphinx.util import logging
from sphinx.util.docfields import DocFieldTransformer, _is_single_paragraph
from typing import Tuple
import warnings


def import_object(docname, kind) -> Tuple[object, str]:
    """
    Extract an object defined by its name including the module name.

    @param      docname     full name of the object
                            (example: ``pyquickhelper.sphinxext.sphinx_docassert_extension.import_object``)
    @param      kind        ``'function'`` or ``'class'`` or ``'kind'``
    @return                 tuple(object, name)
    """
    spl = docname.split(".")
    name = spl[-1]
    context = {}
    if kind == "function":
        modname = ".".join(spl[:-1])
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, name)
        codeobj = compile(code, 'conf.py', 'exec')
    else:
        modname = ".".join(spl[:-2])
        classname = spl[-2]
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, classname)
        codeobj = compile(code, 'conf.py', 'exec')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            exec(codeobj, context, context)
        except Exception as e:
            raise Exception(
                "Unable to compile and execute '{0}'".format(code)) from e

    myfunc = context["myfunc"]
    if kind == "function":
        name = spl[-1]
    elif kind == "method":
        myfunc = getattr(myfunc, spl[-1])
        name = spl[-1]
    elif kind == "class":
        name = spl[-1]
        myfunc = myfunc.__init__
    else:
        raise ValueError("Unknwon value for 'kind'")

    return myfunc, name


def check_typed_make_field(self,
                           types,     # type: Dict[unicode, List[nodes.Node]]
                           domain,    # type: unicode
                           items,     # type: Tuple
                           env=None,  # type: BuildEnvironment
                           # type inspect.Parameters (to check that all parameters are documented)
                           parameters=None,
                           function_name=None,  # str
                           docname=None,  # str
                           kind=None   # str
                           ):
    """
    Overwrite function
    `make_field <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/util/docfields.py#L197>`_.
    Process one argument of a function.

    @param      self            from original function
    @param      types           from original function
    @param      domain          from original function
    @param      items           from original function
    @param      env             from original function
    @param      parameters      list of known arguments for the function or method
    @param      function_name   function name these arguments belong to
    @param      docname         document which contains the object
    @param      kind            tells which kind of object *function_name* is (function, method or class)

    Example of warnings it raises:

    ::

        [docassert] 'onefunction' has no parameter 'a' (in '...project_name\subproject\myexampleb.py').
        [docassert] 'onefunction' has undocumented parameters 'a, b' (...project_name\subproject\myexampleb.py').

    """
    if parameters is None:
        parameters = None
        check_params = {}
    else:
        parameters = list(parameters)
        check_params = {(p if isinstance(p, str) else p.name): 0 for p in parameters}
    logger = logging.getLogger("docassert")

    def check_item(fieldarg, content, logger):
        if fieldarg not in check_params:
            if function_name is not None:
                logger.warning("[docassert] '{0}' has no parameter '{1}' (in '{2}').".format(
                    function_name, fieldarg, docname))
        else:
            check_params[fieldarg] += 1
            if check_params[fieldarg] > 1:
                logger.warning("[docassert] '{1}' of '{0}' is duplicated (in '{2}').".format(
                    function_name, fieldarg, docname))

    if isinstance(items, list):
        for fieldarg, content in items:
            check_item(fieldarg, content, logger)
        mini = None if len(check_params) == 0 else min(check_params.values())
        if mini == 0:
            nodoc = list(sorted(k for k, v in check_params.items() if v == 0))
            if kind == "method":
                nodoc = [_ for _ in nodoc if _ != "self"]
            if len(nodoc) > 0:
                logger.warning("[docassert] '{0}' has undocumented parameters '{1}' (in '{2}').".format(
                    function_name, ", ".join(nodoc), docname))
    else:
        # Documentation related to the return.
        pass


class OverrideDocFieldTransformer:
    """
    Overrides one function with assigning it to a method
    """

    def __init__(self, replaced):
        """
        Constructor

        @param      replaced        should be *DocFieldTransformer.transform*
        """
        self.replaced = replaced

    def override_transform(self, other_self, node):
        """
        Transform a single field list *node*.
        Overwrite function `transform <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/util/docfields.py#L271>`_.
        It only adds extra verification and returns results from the replaced function.

        @param      other_self      the builder
        @param      node            node the replaced function changes or replace

        The function parses the original function and checks that the list of arguments declared
        by the function is the same the list of documented arguments.
        """
        typemap = other_self.typemap
        entries = []
        groupindices = {}  # type: Dict[unicode, int]
        types = {}  # type: Dict[unicode, Dict]

        # step 1: traverse all fields and collect field types and content
        for field in node:
            fieldname, fieldbody = field
            try:
                # split into field type and argument
                fieldtype, fieldarg = fieldname.astext().split(None, 1)
            except ValueError:
                # maybe an argument-less field type?
                fieldtype, fieldarg = fieldname.astext(), ''
            if fieldtype != "param":
                continue
            typedesc, is_typefield = typemap.get(fieldtype, (None, None))

            # sort out unknown fields
            if typedesc is None or typedesc.has_arg != bool(fieldarg):
                # either the field name is unknown, or the argument doesn't
                # match the spec; capitalize field name and be done with it
                new_fieldname = fieldtype[0:1].upper() + fieldtype[1:]
                if fieldarg:
                    new_fieldname += ' ' + fieldarg
                fieldname[0] = nodes.Text(new_fieldname)
                entries.append(field)
                continue

            typename = typedesc.name

            # collect the content, trying not to keep unnecessary paragraphs
            if _is_single_paragraph(fieldbody):
                content = fieldbody.children[0].children
            else:
                content = fieldbody.children

            # if the field specifies a type, put it in the types collection
            if is_typefield:
                # filter out only inline nodes; others will result in invalid
                # markup being written out
                content = [n for n in content if isinstance(n, nodes.Inline) or
                           isinstance(n, nodes.Text)]
                if content:
                    types.setdefault(typename, {})[fieldarg] = content
                continue

            # also support syntax like ``:param type name:``
            if typedesc.is_typed:
                try:
                    argtype, argname = fieldarg.split(None, 1)
                except ValueError:
                    pass
                else:
                    types.setdefault(typename, {})[argname] = [
                        nodes.Text(argtype)]
                    fieldarg = argname

            translatable_content = nodes.inline(
                fieldbody.rawsource, translatable=True)
            translatable_content.document = fieldbody.parent.document
            translatable_content.source = fieldbody.parent.source
            translatable_content.line = fieldbody.parent.line
            translatable_content += content

            # Import object, get the list of parameters
            docs = fieldbody.parent.source.split(":docstring of")[-1].strip()

            myfunc = None
            name = None
            funckind = None
            function_name = None
            excs = []
            for kind in ("function", "method", "class"):
                try:
                    myfunc, name = import_object(docs, kind)
                    funckind = kind
                    function_name = name
                    break
                except Exception as e:
                    # not this kind
                    excs.append(e)

            if myfunc is None:
                if len(excs) > 0:
                    reasons = "\n".join("   {0}".format(e) for e in excs)
                else:
                    reasons = "unknown"
                logger = logging.getLogger("docassert")
                logger.warning(
                    "[docassert] unable to import object '{0}', reasons:\n{1}".format(docs, reasons))
                myfunc = None

            if myfunc is None:
                signature = None
                parameters = None
            else:
                try:
                    signature = inspect.signature(myfunc)
                    parameters = signature.parameters
                except TypeError:
                    logger = logging.getLogger("docassert")
                    logger.warning(
                        "[docassert] unable to get signature of '{0}'.".format(docs))
                    signature = None
                    parameters = None

            # grouped entries need to be collected in one entry, while others
            # get one entry per field
            if typedesc.is_grouped:
                if typename in groupindices:
                    group = entries[groupindices[typename]]
                else:
                    groupindices[typename] = len(entries)
                    group = [typedesc, []]
                    entries.append(group)
                entry = typedesc.make_entry(fieldarg, [translatable_content])
                group[1].append(entry)
            else:
                entry = typedesc.make_entry(fieldarg, [translatable_content])
                entries.append([typedesc, entry])

        # step 2: all entries are collected, check the parameters list.
        try:
            env = other_self.directive.state.document.settings.env
        except AttributeError as e:
            logger = logging.getLogger("docassert")
            logger.warning("[docassert] {0}".format(e))
            env = None

        docname = fieldbody.parent.source.split(':docstring')[0]

        for entry in entries:
            if isinstance(entry, nodes.field):
                # raise NotImplementedError()
                logger = logging.getLogger("docassert")
                logger.warning(
                    "[docassert] unable to checl [nodes.field] {0}".format(entry))
            else:
                fieldtype, content = entry
                fieldtypes = types.get(fieldtype.name, {})
                check_typed_make_field(other_self, fieldtypes, other_self.directive.domain,
                                       content, env=env, parameters=parameters,
                                       function_name=function_name, docname=docname,
                                       kind=funckind)

        return self.replaced(other_self, node)


def setup(app):
    """
    Setup for ``docassert`` extension (sphinx).
    This changes ``DocFieldTransformer.transform`` and replaces
    it by a function which calls the current function and does
    extra checking on the list of parameters.

    .. todoext::
        :title: check parameters list in documentation
        :tag: done
        :hidden: true
        :date: 2017-07-02
        :cost: 3
        :issue: 49
        :release: 1.5
    """
    inst = OverrideDocFieldTransformer(DocFieldTransformer.transform)

    def local_transform(me, node):
        return inst.override_transform(me, node)

    DocFieldTransformer.transform = local_transform
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}