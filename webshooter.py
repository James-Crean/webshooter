#!/usr/bin/env python3

import getpass
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import yaml

if sys.version_info[0] == 2:
  if raw_input("""I was written in Python 3.x, but you're running me with Python 2.x! I was NOT
tested with this version. Run anyway? [y/N] """).lower() != "y":
    sys.exit()

class WebshooterSite:
  def __init__(self):
    self.longname  = None
    self.shortname = None
    self.template  = None
    self.color     = None
    self.pages     = None

  @property
  def yaml(self):
    site_yaml = dict()
    site_yaml["context"] = dict()
    site_yaml["context"]["data"] = dict()
    site_yaml["context"]["data"]["author"] = dict()
    site_yaml["context"]["data"]["menu"] = list()
    site_yaml["plugins"] = list()
    site_yaml["mode"] = "development"
    site_yaml["media_url"] = "media"
    site_yaml["context"]["data"]["site_title"] = site.longname
#   site_yaml["context"]["data"]["author"]["name"] = getpass.getuser()
    site_yaml["context"]["data"]["nav_hover"] = True
    site_yaml["context"]["data"]["home_url"] = "index.html"
    site_yaml["plugins"].append("hyde.ext.plugins.meta.MetaPlugin")
    site_yaml["plugins"].append("hyde.ext.plugins.auto_extend.AutoExtendPlugin")
    site_yaml["plugins"].append("hyde.ext.plugins.syntext.SyntextPlugin")
    site_yaml["plugins"].append("hyde.ext.plugins.textlinks.TextlinksPlugin")
    site_yaml["context"]["data"]["menu"].append({"title": "Home", "url": "index.html"})
    for p in site.pages:
      filename = p.lower().replace(" ", "-") + ".html"
      site_yaml["context"]["data"]["menu"].append({"title": p, "url": filename})
      shutil.copy(site.shortname + "/content/blank.html", site.shortname + "/content/" + filename)
      replace(site.shortname + "/content/" + filename, "Page name", p)
    return yaml.dump(site_yaml)


longname_prompt = """Your website will have two names.
The longname is what users will see. It can have spaces.
A good longname is 'My First Website'. Enter the longname now."""

shortname_prompt = """The shortname is used to name the site on the back end. By convention it should
be lowercase and use hyphens as spaces. A good shortname is 'my-first-website'.
Enter the shortname now."""

description_prompt = """The description is displayed in your site's header, below the longname. Enter
the description now."""

templates = {1: ("bootstrap", "github.com/aims-group/hyde-bootstrap"),
             2: ("one.5lab",  "github.com/aims-group/one.5lab")}
#            3: ("tshirt",    "github.com/aims-group/tshirt"),
template_prompt = "What template to use?"
for k,t in templates.items():
  template_prompt += "\n  " + str(k) + ": " + t[0] + " (" + t[1] + ")"

color_prompt = """You can choose a dominate color to use for this template. Enter one in hex color
format (#RRGGBB)."""

pages_prompt = """What pages will exist?
  You can change these later. Do not include external links you want in nav.
  Separate pages with commas. Enter pages in longname format; shortnames will be
  generated automatically."""

logo_prompt = """Specify a path to a logo which will be copied to your site's directory. If you
don't have one yet, just press Return."""

def hyde_gen(path):
  subprocess.Popen(["hyde", "gen"], cwd=path, stdout=subprocess.DEVNULL)
  print("Complete! Now open\n\n  " + os.path.abspath(path) + "/deploy/index.html\n\nin a web browser.")

# Replaces all occurrances of pattern with subst in file_path
# from http://stackoverflow.com/a/39110/392225
def replace(file_path, pattern, subst):
# Create temp file
  fh, abs_path = tempfile.mkstemp()
  new_file = open(abs_path,'w')
  old_file = open(file_path)
  for line in old_file:
    new_file.write(line.replace(pattern, subst))
# Close temp file
  new_file.close()
  os.close(fh)
  old_file.close()
# Remove original file
  os.remove(file_path)
# Move new file
  shutil.move(abs_path, file_path)

if len(sys.argv) < 2 or sys.argv[1] == "--help":
  print(
  """usage: """ + sys.argv[0] + """ <command> [--help]

commands:
  new              Interactively create a new website
  gen <site_path>  Regenerate the content for the site at `site_path`"""
  )
elif ( len(sys.argv) is 3 and sys.argv[2] == "--help" ) or ( len(sys.argv) is 2 and sys.argv[1] == "gen" ):
  if sys.argv[1] == "new":
    print("""usage: """ + sys.argv[0] + """ new [--help]

  Runs an interactive prompt to create a new website using webshooter. Asks for
  website information such as longname, shortname, template, and a list of pages.
  When the process is complete, the desired template will be cloned into the
  current working directory and your settings for the site will be applied. At
  this point, you should go into this new directory and change the pages in
  the `content` directory to your liking.

  Whenever you change the content of the website and wish for it to be
  regenerated, use `""" + sys.argv[0] + """ gen`.""")
  elif sys.argv[1] == "gen":
    print("""usage: """ + sys.argv[0] + """ gen <site_path>
       """ + sys.argv[0] + """ gen --help

  Regenerates the static content for the website at `site_path` using hyde. You
  should run this whenever any changes are made to the site that you wish to be
  reflected in the deployed version.

  To make changes, edit the files in `layout` and `content`, as well as
  `site.yaml`. After running """ + sys.argv[0] + """, these changes will be
  reflected in the `deploy` directory.""")

else:
  if sys.argv[1] == "new":

    site = WebshooterSite()
    template = ""
    color = ""
    pages = ""

# longname
    print(longname_prompt)
    while not bool(site.longname):
      site.longname = input("longname> ").strip()
# shortname
    print(shortname_prompt)
    while not bool(site.shortname):
      site.shortname = input("shortname> ").strip()
      if re.search("\s", site.shortname) is not None:
        site.shortname = ""
        print("The shortname cannot have spaces, try again.")
      elif os.path.exists(site.shortname):
        if input("A file/folder named " + shortname + " already exists here. Delete the whole thing [y/N]? ").lower() == 'y':
          shutil.rmtree(site.shortname)
        else:
          site.shortname = ""
# Template
    print(template_prompt)
    while site.template not in templates.values():
      try:
        site.template = templates[int(input("template> ").strip())]
      except (KeyError, ValueError):
        pass
# Color (if tshirt)
    if site.template[0] is "tshirt":
      print(color_prompt)
      while site.color is "":
        site.color = input("color> #").strip()
# Pages
    print(pages_prompt)
    while not bool(site.pages):
      site.pages = [ p.strip() for p in input("pages> Home, ").split(",") ]

# Set up the site
    subprocess.call(["git", "clone", "git://" + site.template[1], site.shortname])
    replace(site.shortname + "/content/index.html", "Page name", "Home")
    open(site.shortname + "/site.yaml", "w").write(site.yaml)
    hyde_gen(os.getcwd() + "/" + site.shortname)

  elif sys.argv[1] == "gen":
    hyde_gen(sys.argv[2])

def check_deps():
# python3
# hyde
#   if not, pip
  pass

def set_up_hyde():
  pass
