"""
@file
@brief Functions to call from the notebook

.. versionadded:: 1.1
"""

from IPython.display import Javascript, HTML, display_html


def store_notebook_path(name="theNotebook"):
    """
    return Javascript object to execute in order to store
    the notebook file name into a variable
    available from the notebook

    @param      name        name of the variable
    @return                 Javascript object

    The function uses the following code to get the notebook path::

        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "theNotebook = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);

    Example::

        from pyquickhelper.ipythonhelper import store_notebook_path
        store_notebook_path()

    In another cell::

        theNotebook

    See notebook :ref:`exempleoffixmenurst`.
    Same function as @see fn set_notebook_name_theNotebook.

    .. versionadded:: 1.1
    """
    js = """
        var kernel = IPython.notebook.kernel;
        var body = document.body,
        attribs = body.attributes;
        var command = "{0} = os.path.join(" + "r'"+attribs['data-project'].value+"'," + "r'"+attribs['data-notebook-path'].value+"'," + "r'"+attribs['data-notebook-name'].value+"')";
        kernel.execute(command);
        """.replace("        ", "").format(name)
    return Javascript(js)


def set_notebook_name_theNotebook():
    """
    This function must be called from the notebook
    you want to know the name. It relies on
    a javascript piece of code. It populates
    the variable ``theNotebook`` with the notebook name.

    This solution was found at
    `How to I get the current IPython Notebook name <http://stackoverflow.com/questions/12544056/how-to-i-get-the-current-ipython-notebook-name>`_.

    The function can be called in a cell.
    The variable ``theNotebook`` will be available in the next cells.

    Same function as @see fn store_notebook_path.

    .. versionadded:: 1.1
    """
    code = """var kernel = IPython.notebook.kernel;
              var body = document.body, attribs = body.attributes;
              var command = "theNotebook = " + "'"+attribs['data-notebook-name'].value+"'";
              kernel.execute(command);""".replace("              ", "")

    def get_name():
        from IPython.core.display import Javascript, display
        display(Javascript(code))
    return get_name()


def add_notebook_menu(menu_id="my_id_menu_nb", raw=False, format="html"):
    """
    add javascript and HTML to the notebook which gathers all in the notebook and builds a menu

    @param      menu_id     menu_id
    @param      raw         raw HTML and Javascript
    @param      format      *html* or *rst*
    @return                 HTML object
    
    In a notebook, it is easier to do by using a magic command 
    ``%%html`` for the HTML and another one
    ``%%javascript`` for the Javascript.
    This function returns a full text with HTML and
    Javascript.
    
    If the format is RST, the menu can be copied/pasted in a text cell.
    """
    if format == "html":
        html = '<div id="{0}">run previous cell</div>'.format(menu_id)
        js = """
            var anchors = document.getElementsByClassName("anchor-link");
            var menu = document.getElementById("__MENUID__");
            menu.innerHTML="r";
            var i;
            var text_menu = "<ul>";
            for (i = 0; i < anchors.length; i++) {
                var title = anchors[i].parentNode.textContent;
                title = title.substring(0,title.length-1);
                var href = anchors[i].href.split('#')[1];
                text_menu += '<li><a href="#' + href + '">' + title + '</a></li>';
            }
            text_menu += "</ul>"
            menu.innerHTML=text_menu;
            """.replace("        ", "").replace("__MENUID__", menu_id)

        full = "{0}\n<script>{1}</script>".format(html, js)
        if raw:
            return full
        else:
            return HTML(full)
    elif format == "rst":
        html = '<div id="{0}">run previous cell</div>'.format(menu_id)
        js = """
            var anchors = document.getElementsByClassName("anchor-link");
            var menu = document.getElementById("__MENUID__");
            menu.innerHTML="r";
            var i;
            var text_menu = "<pre>";
            for (i = 0; i < anchors.length; i++) {
                var title = anchors[i].parentNode.textContent;
                title = title.substring(0,title.length-1);
                var href = anchors[i].href.split('#')[1];
                text_menu += '* [' + title + '](#' + href + ')\\n';
            }
            text_menu += "</pre>"
            menu.innerHTML=text_menu;
            """.replace("        ", "").replace("__MENUID__", menu_id)

        full = "{0}\n<script>{1}</script>".format(html, js)
        if raw:
            return full
        else:
            return HTML(full)
    else:
        raise ValueError("format must be html or rst")
        
