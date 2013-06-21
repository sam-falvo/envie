#!/usr/bin/env python

class RemoteRepo(object):
  def __init__(self, dv, hn):
    self.default_version = dv
    self.host_name = hn

  def defaultVersion(self):
    return self.default_version

  def installVersion(self, org, pkg, ver, path=None):
    if not path:
      path = "src/%s/%s" % (self.host_name, org)

    cmds = """cd $GOPATH
mkdir -p %s
cd %s
%s
%s
""" % (
  path,
  path,
  self.downloader(org, pkg),
  self.versioner(ver)
)
    print cmds


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
  "github.com": GitRepo("master", "github.com"),
  "bitbucket.org": HgRepo("trunk", "bitbucket.org"),
  "intranet.example.com": GitRepo("master", "intranet.example.com"),
}

class StateMachine(object):
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
  s = StateMachine()
  try:
    with file("dependencies.envie") as depsFile:
      for line in depsFile:
        line = line.strip()
        if len(line):
          (cmd, param) = line.split()
          s.interpret(cmd, param)
  except IOError:
    # Envie allows for an optional dependencies file.  If it's missing, that's OK.
    pass

if __name__ == '__main__':
  main()

