"""
@brief
@file Batch file use to automate some of the tasks (setup, unit tests, help, pypi).

.. versionadded:: 1.1
"""
import sys


def _sversion():
    return "PY%d%d" % sys.version_info[:2]

#################
#: stop if error
#################
windows_error = "if %errorlevel% neq 0 exit /b %errorlevel%"

#################
#: prefix
#################
windows_prefix = """
@echo off
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe=%1
goto start_script:

:default_value_python:
set pythonexe=__PY??_X64__\\python

@echo ~SET pythonexe=%pythonexe%

:start_script:
set current=%~dp0
@echo ~SET current=%current%
""".replace("PY??", _sversion())

#################
#: prefix 27
#################
windows_prefix_27 = """
@echo off
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe27=%1
goto start_script:

:default_value_python:
set pythonexe27=__PY27_X64__\\python
:start_script:
@echo ~SET pythonexe27=%pythonexe27%
"""

#################
#: run unit test 27
#################
windows_unittest27 = """
@echo off
set PYTHONPATH=
@echo ~SET PYTHONPATH=
cd dist_module27\\_unittests

rem errorlevel does not work well in a loop
rem for /d %%d in (ut_*) do (
rem     @echo ~CALL %pythonexe27%\\..\\Scripts\\nosetests.exe -w %%d
rem     %pythonexe27%\\..\\Scripts\\nosetests.exe -w %%d
rem     if %errorlevel% neq 0 exit /b %errorlevel%
rem )

__LOOP_UNITTEST_FOLDERS__

""" + windows_error + "\ncd ..\.."

############
#: copy to local pypiserver
############

copy_to_pypiserver = """
@echo ~LABEL end
rem we copy the wheel on a local folder to let a pypiserver take it
if not exist ..\\..\\local_pypi mkdir ..\\..\\local_pypi
if not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server
@echo ~CALL copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
"""

####################################################
#: build any script for Windows from a virtual environment
####################################################
windows_any_setup_command_base = """
@echo off
if "%1"=="" @echo usage: SCRIPT [pythonpath] [suffix] [command] [...]
set CURRENT_THIS=%~dp0
@echo ~SET CURRENT_THIS=%CURRENT_THIS%

IF EXIST dist del /Q dist\\*.*
IF EXIST build del /Q build\\*.*

if "%2"=="" goto default_value_suffix:
if "%2"=="default" goto default_value_suffix:
set virtual_env_suffix=%2
goto default_value_suffix_next:
:default_value_suffix:
set virtual_env_suffix=_anyenv
:default_value_suffix_next:
@echo ~SET set virtual_env_suffix=%virtual_env_suffix%

if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
goto default_value_next:
:default_value:
set pythonexe=__PY??_X64__\\python
:default_value_next:

echo ###----################################################5
echo ###----################################################5
echo ###----################################################5
echo %pythonexe%
echo ###----################################################5
echo ###----################################################5
echo ###----################################################5
SET ROOT_VIRTUAL_ENV=%CURRENT_THIS%_virtualenv
if not exist %ROOT_VIRTUAL_ENV% mkdir %ROOT_VIRTUAL_ENV%
set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
if not exist %pythonexe%\\..\\Scripts\\virtualenv.exe goto conda_virtual_env:

if exist %virtual_env_py%_vir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_vir%virtual_env_suffix%
mkdir %virtual_env_py%_vir%virtual_env_suffix%

if exist %virtual_env_py%_vir%virtual_env_suffix%\\python goto with_virtual:
set KEEPPATH=%PATH%
@echo ~SET KEEPPATH=%PATH%
set PATH=%pythonexe%\\..;%PATH%
@echo ~SET PATH=%pythonexe%\\..;%PATH%
@echo ~CALL %pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
%pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
@echo ### VIRTUAL ENVIRONMENT CREATED in %virtual_env_py%_vir%virtual_env_suffix%

@echo on
rem _PATH_VIRTUAL_ENV_
@echo off

:with_virtual:
@echo ~LABEL with_virtual
set pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
@echo ~SET pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
set pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
@echo ~SET pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
goto requirements:

:conda_virtual_env:
@echo ~LABEL conda_virtual_env
if exist %virtual_env_py%_condavir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_condavir%virtual_env_suffix%

if exist %virtual_env_py%_condavir%virtual_env_suffix%\\python goto with_virtual_conda:

@echo ~CALL %pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
%pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%

:with_virtual_conda:
@echo ~LABEL with_virtual_conda
set pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
@echo ~SET pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
set pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip
@echo ~SET pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip

:requirements:
@echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
set pythonexe_rel=..\\..\\%pythonexe%.exe
@echo ~SET pythonexe_rel=..\\..\\%pythonexe%.exe
if exist %pythonexe_rel% goto auto_setup_relpath:
set pythonexe_rel=%pythonexe%
@echo ~SET pythonexe_rel=%pythonexe%

:auto_setup_relpath:
@echo ~LABAL auto_setup_relpath
@echo ~CALL %pythonexe_rel% auto_setup_dep.py install
%pythonexe_rel% auto_setup_dep.py install > auto_setup_dep.log
rem if %errorlevel% neq 0 exit /b %errorlevel%
rem we continue to run the script even if it seems to fail
cd ..\\..
@echo #######################################################_auto_setup_dep.py END

@echo #######################################################_requirements_begin
@echo ~SET %pythonpip%
__REQUIREMENTS__
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################_requirements_end

@echo ~SET pythonexe=%pythonexe%
@echo ~CALL %pythonexe% setup.py write_version
%pythonexe% setup.py write_version
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ################# VERSION
more version.txt
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ################# VERSION

@echo #######################################################_PATH
set PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__
@echo ~SET PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__
""".replace("PY??", _sversion())


#################
#: setup_hook for Windows
#################

windows_setup_hook = """
@echo #######################################################_setup_hook
@echo ~CALL %pythonexe% setup.py setup_hook
%pythonexe% setup.py setup_hook
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################_END_BASE
"""

#################
#: build script for Windows
#################

windows_any_setup_command = windows_any_setup_command_base + windows_setup_hook + """
@echo ~CALL %pythonexe% -u setup.py %3 %4 %5 %6 %7 %8 %9
rem set PYTHONPATH=additional_path
%pythonexe% -u setup.py %3 %4 %5 %6 %7 %8 %9
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################6
""" + copy_to_pypiserver

#################
#: call the setup
#################
windows_setup = "rem set PYTHONPATH=additional_path\n%pythonexe% -u setup.py"
jenkins_windows_setup = "%jenkinspythonexe% -u setup.py"

#################
#: build setup script for Windows
#################

windows_build_setup = windows_any_setup_command_base + windows_setup_hook + """
@echo ~CALL %pythonexe% setup.py sdist %2 --formats=gztar,zip --verbose
%pythonexe% setup.py sdist %2 --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ~CALL %pythonexe% setup.py bdist_wheel %2
%pythonexe% setup.py bdist_wheel %2
if %errorlevel% neq 0 exit /b %errorlevel%
""" + copy_to_pypiserver

#################
#: build script MAIN SCRIPT
#################
windows_build = windows_any_setup_command_base + windows_setup_hook + """
@echo #######################################################_unit
@echo ~CALL %pythonexe% -u setup.py unittests
rem set PYTHONPATH=additional_path --> we use a virtual environment here
%pythonexe% -u setup.py unittests
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################6

@echo ~CALL %pythonexe% setup.py clean_pyd
%pythonexe% setup.py clean_pyd
@echo ~CALL %pythonexe% setup.py sdist --formats=gztar,zip --verbose
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ~CALL %pythonexe% setup.py bdist_wininst --plat-name=win-amd64
%pythonexe% setup.py bdist_wininst --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ~CALL %pythonexe% setup.py bdist_msi
%pythonexe% setup.py bdist_msi
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ~CALL %pythonexe% setup.py bdist_wheel
%pythonexe% setup.py bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################7

:documentation:
@echo ~LABEL documentation
@echo ~CALL %pythonexe% -u setup.py build_sphinx
%pythonexe% -u setup.py build_sphinx
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################8

:copyfiles:
@echo ~LABEL copyfiles
if not exist dist\\html mkdir dist\\html
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
if not exist dist\\epub mkdir dist\\epub
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\epub dist\\epub
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\epub dist\\epub
@echo ~COPY chm
if exist _doc\\sphinxdoc\\build\\htmlhelp copy _doc\\sphinxdoc\\build\\htmlhelp\\*.chm dist\\html
@echo ~COPY pdf
if exist _doc\\sphinxdoc\\build\\latex xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\latex\\*.pdf dist\\html
if %errorlevel% neq 0 exit /b %errorlevel%

:end:
""".replace("PY??", _sversion()) + copy_to_pypiserver

#################
#: build script for Windows BASE + virtual environment
#################

copy_sphinx_to_dist = """
if not exist dist\\html mkdir dist\\html
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
if not exist dist\\epub mkdir dist\\epub
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\epub dist\\epub
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\epub dist\\epub
@echo ~COPY chm
if exist _doc\\sphinxdoc\\build\\htmlhelp copy _doc\\sphinxdoc\\build\\htmlhelp\\*.chm dist\\html
@echo ~COPY pdf
if exist _doc\\sphinxdoc\\build\\latex xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\latex\\*.pdf dist\\html
if %errorlevel% neq 0 exit /b %errorlevel%
"""

#################
#: notebooks
#################
windows_notebook = """
@echo off
if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
goto nextn:

:default_value:
@echo ~LABEL default_value
set pythonexe=__PY??_X64__
@echo ~SET pythonexe=__PY??_X64__

:nextn:
@echo ~LABEL nextn
set current=%~dp0
set path=%path%;%pythonexe%;%pythonexe%\\Scripts
@echo ~SET path=%path%;%pythonexe%;%pythonexe%\\Scripts
@echo ~CALL jupyter-notebook --notebook-dir=_doc\\notebooks --matplotlib=inline
set PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__
@echo ~SET PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__
jupyter-notebook --notebook-dir=_doc\\notebooks --matplotlib=inline
""".replace("PY??", _sversion())

#################
#: publish a module
#################
windows_publish = """
%pythonexe% setup.py rotate --match=.zip --keep=1
%pythonexe% setup.py rotate --match=.tar.gz --keep=10
%pythonexe% setup.py rotate --match=.whl --keep=10
rem %pythonexe% setup.py sdist register
%pythonexe% setup.py sdist --formats=gztar upload
%pythonexe% setup.py bdist_wheel upload
"""

#################
#: publish the documentation
#################
windows_publish_doc = """
%pythonexe% -u setup.py upload_docs --upload-dir=dist/html
"""

#################
#: run a pypi server
#################
windows_pypi = """
set pythonexe=__PY??_X64__
@echo ~SET pythonexe=__PY??_X64__

if "%2"=="" goto default_port:
if "%2"=="default" goto default_port:
set portpy=%2
@echo ~SET portpy=%2
goto run:

:default_port:
@echo ~LABEL default_port
set portpy=__PORT__
@echo ~SET portpy=__PORT__

:run:
@echo ~LABEL run
@echo ~CALL %pythonexe%\Scripts\pypi-server.exe -u -p %portpy% --disable-fallback ..\\..\\local_pypi\\local_pypi_server
%pythonexe%\Scripts\pypi-server.exe -u -p %portpy% --disable-fallback ..\\..\\local_pypi\\local_pypi_server
""".replace("PY??", _sversion())

#################
#: script for Jenkins
#################
windows_jenkins = "set jenkinspythonexe=__PYTHON__\n@echo ~SET jenkinspythonexe=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_windows_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    windows_error + "\nauto_unittest_setup_help.bat %jenkinspythonexe% __SUFFIX__\n" + \
    windows_error

windows_jenkins_any = "set jenkinspythonexe=__PYTHON__\n@echo ~SET jenkinspythonexe=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_windows_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    windows_error + "\nauto_cmd_any_setup_command.bat %jenkinspythonexe% __SUFFIX__ __COMMAND__\n" + \
    windows_error

####################
#: script for Jenkins 27
####################
windows_jenkins_unittest27 = """
@echo off
set CURRENT_PATH=%WORKSPACE%
@echo ~SET CURRENT_PATH=%WORKSPACE%
set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27
set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
if exist %virtual_env_py%_conda27vir rmdir /Q /S %virtual_env_py%_conda27vir
@echo ~CALL %jenkinspythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_conda27vir --clone %jenkinspythonexe%\\.. --offline
%jenkinspythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_conda27vir --clone %jenkinspythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%
set jenkinspythonexe=%virtual_env_py%_conda27vir\\python
@echo ~SET jenkinspythonexe=%virtual_env_py%_conda27vir\\python
set jenkinspythonpip=%virtual_env_py%_conda27vir\\Scripts\\pip
@echo ~SET jenkinspythonpip=%virtual_env_py%_conda27vir\\Scripts\\pip

:requirements:
@echo ~LABEL requirements
@echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
set pythonexe_rel=..\\..\\%jenkinspythonexe%.exe
@echo ~SET pythonexe_rel=..\\..\\%jenkinspythonexe%.exe
if exist %pythonexe_rel% goto auto_setup_relpath:
set pythonexe_rel=%jenkinspythonexe%
@echo ~SET pythonexe_rel=%jenkinspythonexe%

:auto_setup_relpath:
@echo ~LABEL auto_setup_relpath
@echo ~CALL %pythonexe_rel% auto_setup_dep.py install
%pythonexe_rel% auto_setup_dep.py install
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..\\..
if %errorlevel% neq 0 exit /b %errorlevel%

@echo #######################################################_requirements_begin
echo ~SET %jenkinspythonpip%
""".replace("PY??", _sversion())


windows_jenkins_27 = [
    "set jenkinspythonexe=__DEFAULTPYTHON__\n@echo ~SET jenkinspythonexe=__DEFAULTPYTHON__\n" +
    "\n__PACTHPQb__\n" +
    jenkins_windows_setup + " build_script\n" +
    windows_error +
    "\n@echo ~CALL %jenkinspythonexe% setup.py setup_hook\n%jenkinspythonexe% setup.py setup_hook\n" +
    windows_error +
    "\nauto_setup_copy27.bat %jenkinspythonexe%\n" +
    windows_error,
    "\n__PACTHPQe__\n" +
    "set jenkinspythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    windows_jenkins_unittest27 +
    "\n\n__REQUIREMENTS__\n\n" +
    "\nauto_cmd_run27.bat %jenkinspythonexe%\n" + windows_error,
    "set jenkinspythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    "set CURRENT_PATH=%WORKSPACE%\n@echo ~SET CURRENT_PATH=%WORKSPACE%\n" +
    "set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27\n" +
    "set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__\n@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__\n" +
    "set jenkinspythonexe=%virtual_env_py%_conda27vir\\python\n@echo ~SET jenkinspythonexe=%virtual_env_py%_conda27vir\\python\n" +
    "\nauto_cmd_build27.bat %jenkinspythonexe%\n" + windows_error,
    "copy dist_module27\\dist\\*.whl ..\\..\\local_pypi\\local_pypi_server"]

##################
#: auto setup
##################
setup_script_dependency_py = """
import sys
from distutils.core import setup, Extension
import distutils.sysconfig as SH
from setuptools import find_packages

project_var_name = "dependencies___MODULE__"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name

if "Anaconda" not in sys.version or sys.version_info[0] == 2:
    jup = ["IPython", "jupyter"]
else:
    jup = []

setup(
    name=project_var_name,
    version=versionPython,
    install_requires=[
        "autopep8",
        "numpy",
        "dateutils",
        "matplotlib",
        "sphinx",
        "pandas",
        "sphinxjp.themes.revealjs",
        "dateutils",
        "docutils", ] + jup,
)
"""
#########################
#: copy27
#########################

copy_dist_to_local_pypi = """
if not exist ..\\..\\local_pypi mkdir ..\\..\\local_pypi
if not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server
copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
"""

###############
#: blog post
###############
windows_blogpost = """
%pythonexe% auto_rss_server.py
"""

#####################
#: documentation server
#####################
windows_docserver = """
%pythonexe% auto_doc_server.py
"""

########
#: pyproj
########

pyproj_template = """
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003" ToolsVersion="4.0">
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <SchemaVersion>2.0</SchemaVersion>
    <ProjectGuid>__GUID__</ProjectGuid>
    <ProjectHome>.</ProjectHome>
    <SearchPath>
    </SearchPath>
    <WorkingDirectory>.</WorkingDirectory>
    <OutputPath>.</OutputPath>
    <Name>__NAME__</Name>
    <RootNamespace>__NAME__</RootNamespace>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Debug' ">
    <DebugSymbols>true</DebugSymbols>
    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Release' ">
    <DebugSymbols>true</DebugSymbols>
    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
  </PropertyGroup>
  <ItemGroup>
__INCLUDEFILES__
  </ItemGroup>
  <ItemGroup>
__INCLUDEFOLDERS__
  </ItemGroup>
  <PropertyGroup>
    <VisualStudioVersion Condition="'$(VisualStudioVersion)' == ''">10.0</VisualStudioVersion>
    <PtvsTargetsFile>$(MSBuildExtensionsPath32)\\Microsoft\\VisualStudio\\v$(VisualStudioVersion)\\Python Tools\\Microsoft.PythonTools.targets</PtvsTargetsFile>
  </PropertyGroup>
  <Import Condition="Exists($(PtvsTargetsFile))" Project="$(PtvsTargetsFile)" />
  <Import Condition="!Exists($(PtvsTargetsFile))" Project="$(MSBuildToolsPath)\\Microsoft.Common.targets" />
  <!-- Uncomment the CoreCompile target to enable the Build command in
       Visual Studio and specify your pre- and post-build commands in
       the BeforeBuild and AfterBuild targets below. -->
  <!--<Target Name="CoreCompile" />-->
  <Target Name="BeforeBuild">
  </Target>
  <Target Name="AfterBuild">
  </Target>
</Project>
"""
