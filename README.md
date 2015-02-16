sd_web
======

Species delimitation web server

Provide web interface for PTP and GMYC

Installation
------------

### Webserver
Clone the repository to {your_install_path}
Install the python requirements
`pip install -r {your_install_path}/sd_server/requirements_django.txt`

### Software
Clone the repository to {your_software_path} - yopu can use the same install location as for the webserver.
`pip install -r {your_install_path}/sd_server/requirements_apps.txt`
`Rscript sd_server/requirements.R`

This of course assumes, that pip and R are available.
`easy_install pip` should install pip.
`apt-get install r-base-core` should install R on ubuntu - similar packages are available for other Linux distributions.
Additionally, PTP uses [ete2](http://pythonhosted.org/ete2/) for visualiziation which in turn requires PyQt4 which cannot be installed via pip, but through the package manager of your OS:
`apt-get install python-qt4`.
You can also compile it yourself [PyQt in virtualenv](http://amyboyle.ninja/Python-Qt-and-virtualenv-in-linux/).
An X-server is also required for ete2. Installation and setup are described here:
http://pythonhosted.org/ete2/tutorial/tutorial_webplugin.html#servers
The ptp-webserver code currently assumes, that [Xvfb](http://de.wikipedia.org/wiki/Xvfb) is installed: `apt-get install xvfb` which also works on a cluster environment nicely without having all xorg-server components installed and running.

Deployment
----------
This [django](https://www.djangoproject.com/) project uses [django-configurations](http://django-configurations.readthedocs.org/)
Change sd_server/sd_server/config/production.py pr server.py by changing any of the configuration variables. 
Accordingly - go to manage.py and wsgi.py and change the DJANGO_CONFIGURATION to the configuration class you want to use.

If you use apache to deploy dajngo, please consider using [mod_wsgi](https://code.google.com/p/modwsgi/)

create a /etc/apache2/sites-available/ptp.conf and add this
```xml
<VirtualHost *:80>
    WSGIDaemonProcess sd_server python-path={your_install_path}/sd_server
    WSGIProcessGroup sd_server
    WSGIScriptAlias / {your_install_path}/sd_server/sd_server/wsgi.py
    Alias /static/ {your_install_path}/sd_server/static/
    
    <Directory {your_install_path}/sd_server/static/>
        Require all granted
    </Directory>
</VirtualHost>
```

GMYC
====
the gmyc Rscript can be used independently
$Rscript gmyc.script.R tree method

input: an input tree in newick or nexus format (its name should end with ".tre" or ".nex".
method: type of method, s for single and m for multiple threshold.

(you can make it executable if Rscript is installed as /usr/bin/Rscript, like other linux scripts)

It outputs following files.

xxxx_list: a tab-delimited text file of delimitation. it is an output of the spec.list function.
xxxx_summary: a text file of summary of analysis from summary.gmyc.
xxxx_plot.pdf: plots in pdf format.
xxxx_plot.png: plots in png format.
