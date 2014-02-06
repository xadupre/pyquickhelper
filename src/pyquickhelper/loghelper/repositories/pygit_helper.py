"""
@file
@brief  Uses git to get version number.
"""

import os,sys,datetime
import xml.etree.ElementTree as ET

from ..flog import fLOG, run_cmd
from ..convert_helper import str_to_datetime

def IsRepo(location, commandline = False):
    """
    says if it a repository GIT
    
    @param      location        (str) location
    @param      commandline     (bool) use commandline or not
    @return                     bool
    """
    if location == None :
        location = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..", "..")))
        
    try :
        v = get_repo_version(location, commandline)
        return True
    except :
        return False

class RepoFile :
    """
    mimic a GIT file
    """
    def __init__ (self, **args) :
        """
        constructor
        @param   args       list of members to add
        """
        for k,v in args.items() :
            self.__dict__[k] = v
            
    def __str__(self):
        """
        usual
        """
        return self.name

def repo_ls(full, commandline = False):
    """
    run ``ls`` on a path
    @param      full            full path
    @param      commandline use command line instead of pysvn
    @return                     output of client.ls
    """
    
    if not commandline :
        try :
            raise NotYetImplemented()
        except Exception as e :
            return repo_ls(full, True)
    else :
        if sys.platform.startswith("win32") :
            cmd = r'"C:\Program Files (x86)\Git\bin\git"' 
        else :
            cmd = 'git' 
        
        cmd += " ls-tree -r HEAD \"%s\"" % full
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "strict",
                            encoding = sys.stdout.encoding,
                            change_path = os.path.split(full)[0] if os.path.isfile(full) else full)
        if len(err) > 0 :
            fLOG ("problem with file ", full, err)
            raise Exception(err)

        res = [ RepoFile(name=os.path.join(full,_.strip().split()[-1])) for _ in out.split("\n") if len(_) > 0]
        return res
            
def __get_version_from_version_txt(path) :
    """
    private function, tries to find a file ``version.txt`` which should
    contains the version number (if svn is not present)
    @param      path        folder to look, it will look to the the path of this file,
                            some parents directories and finally this path
    @return                 the version number
    
    @warning If ``version.txt`` was not found, it throws an exception.
    """
    file = os.path.split(__file__)[0]
    pathes = [ file,
               os.path.join(file, ".."),
               os.path.join(file, "..", ".."),
               os.path.join(file, "..", "..", ".."),
               path ]
    for p in pathes :
        fp = os.path.join(p, "version.txt")
        if os.path.exists (fp) :
            with open(fp, "r") as f :
                return int(f.read().strip(" \n\r\t")) 
    raise FileNotFoundError("unable to find version.txt in\n" + "\n".join(pathes))
    
def get_repo_log (path = None, file_detail = False, commandline = False) :
    """
    get the latest changes operated on a file in a folder or a subfolder
    @param      path            path to look
    @param      file_detail     if True, add impacted files
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     list of changes, each change is a list of 4-uple:
                                    - author
                                    - change number (int)
                                    - date (datetime)
                                    - comment
                    
    The function use a command line if an error occured. It uses the xml format:
    @code
    <logentry revision="161">
        <author>xavier dupre</author>
        <date>2013-03-23T15:02:50.311828Z</date>
        <msg>pyquickhelper: first version</msg>
    </logentry>
    @endcode
    """
    if path == None :
        path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..")))
        
    if not commandline :
        try :
            raise NotYetImplemented()
        except Exception as e :
            return get_repo_log(path, file_detail, True)
    else :
        if sys.platform.startswith("win32") :
            cmd = r'"C:\Program Files (x86)\Git\bin\git"' 
        else :
            cmd = 'git' 

        cmd += ' log --pretty=format:"<logentry revision=\\"%h\\"><author>%an</author><date>%ci</date><msg>%s</msg></logentry>" ' + path
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "strict",
                            encoding = sys.stdout.encoding,
                            change_path = os.path.split(path)[0] if os.path.isfile(path) else path)
        if len(err) > 0 :
            fLOG ("problem with file ", path, err)
            raise Exception(err)

        out = out.replace("\n\n","\n")
        out = "<xml>%s</xml>"%out
        root = ET.fromstring(out)
        res = []
        for i in root.iter('logentry'):
            revision    = i.attrib['revision'].strip()
            author      = i.find("author").text.strip()
            t           = i.find("msg").text
            msg         = t.strip() if t != None else "-"
            sdate       = i.find("date").text.strip()
            dt          = str_to_datetime(sdate.replace("T"," ").strip("Z "))
            row         = [author, revision, dt, msg ]
            res.append(row)
        return res
            
    message = []
    for info in log:
        message.append ( ( "",
                           info.revision.number, 
                           datetime.datetime.utcfromtimestamp(info.date),
                           info.message) )
        if file_detail :
            for i,pt in enumerate(info.changed_paths) :
                message.append( ("file",
                                 info.revision.numbe, 
                                 pt.data["action"], 
                                 pt.data["path"]) )
                if i > 100 :
                    message.append ("       ...")
                    break
            
    return message
            
def get_repo_version (path = None, commandline = False) :
    """
    get the latest check in number for a specific path
    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer (check in number)
    """
    if path == None :
        path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..")))
        
    if not commandline :
        try :
            raise NotYetImplemented()
        except Exception as e :
            return get_repo_version(path, True)
    else :
        if sys.platform.startswith("win32") :
            cmd = r'"C:\Program Files (x86)\Git\bin\git" log --format="%h"'   # %H for full commit hash
        else :
            cmd = 'git log --format="%H"' 

        if path != None : cmd += " \"%s\"" % path
        
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "strict",
                            encoding = sys.stdout.encoding,
                            change_path = os.path.split(path)[0] if os.path.isfile(path) else path)
                                                                            
        if len(err) > 0 :
            fLOG ("problem with file ", path, err)
            raise Exception(err)
        lines = out.split("\n")
        lines = [ _ for _ in lines if len(_) > 0 ]
        res = lines[0]
        
        if len(res) == 0 :
            raise Exception("the command 'git help' should return something")
                
        return res
            

    