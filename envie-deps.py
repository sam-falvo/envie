#!/usr/bin/env python

import os
import sys
import urllib2



def curl(url):
  u = urllib2.urlopen(url)
  content = u.read()
  u.close()
  return content

class RemoteRepo(object):
  def __init__(self, dv, hn, rn):
    self.default_version = dv
    self.host_name = hn
    self.raw_host_name = rn

  def defaultVersion(self):
    return self.default_version

  def rawFileUrl(self, org, pkg, version, fname):
    return "https://%s/%s/%s/%s/%s" % (self.raw_host_name, org, pkg, version, fname)

  def cmd(self, c):
    print(c)
    os.system(c)

  def installVersion(self, org, pkg, ver, path=None):
    if not path:
      path = "src/%s/%s" % (self.host_name, org)
    gopath = os.getenv("GOPATH")
    self.cmd("cd %s && mkdir -p %s" % (gopath, path))
    self.cmd("cd %s && %s" % (path, self.downloader(org, pkg)))
    self.cmd("cd %s/%s && %s" % (path, pkg, self.versioner(ver)))


class GitRepo(RemoteRepo):
  def __init__(self, *args, **kwArgs):
    super(GitRepo, self).__init__(*args, **kwArgs)

  def downloader(self, org, pkg):
    return "git clone git@%s:%s/%s" % (self.host_name, org, pkg)

  def versioner(self, ver):
    return "git checkout %s" % (ver)

class HgRepo(RemoteRepo):
  def __init__(self, *args, **kwArgs):
    super(HgRepo, self).__init__(*args, **kwArgs)

  def downloader(self, org, pkg):
    return "hg clone https://%s/%s/%s" % (self.host_name, org, pkg)

  def versioner(self, ver):
    return "hg checkout %s" % (ver)

_REPOS = {
  "github.com": GitRepo("master", "github.com", "raw.github.com"),
  "bitbucket.org": HgRepo("trunk", "bitbucket.org", "bitbucket.org"),
  "intranet.example.com": GitRepo("master", "intranet.example.com", "raw.example.com"),
}

class DependenciesStateMachine(object):
  def __init__(self):
    self.setRepo("github.com")
    self.deps = ""

  def setRepo(self, r):
    self.repo = _REPOS[r]
    self.org = None
    self.version = self.repo.defaultVersion()
    self.path = None

  def setOrg(self, o):
    self.org = o
    self.path = None

  def setVersion(self, v):
    self.version = v

  def setPath(self, p):
    self.path = p

  def installPackage(self, p):
    url = self.repo.rawFileUrl(self.org, p, self.version, "dependencies.envie")
    print(">> GET %s" % url)
    try:
      self.deps = "%s\n%s" % (self.deps, str(curl(url)))
    except IOError:
      # If not found, not a problem; it just means the dep is a leaf.
      pass
    finally:
      self.setVersion(self.repo.defaultVersion())

  def dependencies(self):
    return self.deps

  def interpret(self, cmd, param):
    # Ignore errors for now.
    if cmd == "repo":
      self.setRepo(param)
    elif cmd == "org":
      self.setOrg(param)
    elif cmd == "ver":
      self.setVersion(param)
    elif cmd == "pkg":
      self.installPackage(param)
    elif cmd == "dir":
      self.setPath(param)

class InstallStateMachine(object):
  def __init__(self):
    self.setRepo("github.com")

  def setRepo(self, r):
    self.repo = _REPOS[r]
    self.org = None
    self.version = self.repo.defaultVersion()
    self.path = None

  def setOrg(self, o):
    self.org = o
    self.path = None

  def setVersion(self, v):
    self.version = v

  def setPath(self, p):
    self.path = p

  def installPackage(self, p):
    self.repo.installVersion(self.org, p, self.version, self.path)
    self.version = self.repo.defaultVersion()

  def interpret(self, cmd, param):
    # Ignore errors for now.
    # This means a "command" of # is a comment by convenience.
    if cmd == "repo":
      self.setRepo(param)
    elif cmd == "org":
      self.setOrg(param)
    elif cmd == "ver":
      self.setVersion(param)
    elif cmd == "pkg":
      self.installPackage(param)
    elif cmd == "dir":
      self.setPath(param)

def main():
  # We absolutely must have GOPATH set for this code to work.  Sorry.
  if not os.getenv("GOPATH"):
    sys.stderr.write("You need to have GOPATH set before running this code.\n")
    sys.exit(1)

  # First, we process our immediate dependencies to build the complete set of deps.

  s = DependenciesStateMachine()
  try:
    with file("dependencies.local") as depsFile:
      for line in depsFile:
        line = line.strip()
        if len(line):
          (cmd, param) = line.split()
          s.interpret(cmd, param)
    file("dependencies.envie", "w").write(s.dependencies())
  except IOError:
    pass

  # We have all the deps for our deps, but not the deps we depend on locally.
  # Add those here.

  os.system("echo '*****'")
  os.system("cat dependencies.envie")
  os.system("echo '*****'")

  file("dependencies.envie", "a").write(file("dependencies.local", "r").read())

  # Now install all the deps, if they're not already present.

  s = InstallStateMachine()
  with file("dependencies.envie") as depsFile:
    for line in depsFile:
      line = line.strip()
      if len(line):
        (cmd, param) = line.split()
        s.interpret(cmd, param)

if __name__ == '__main__':
  main()

