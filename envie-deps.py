#!/usr/bin/env python

class GitHubRepo(object):
  def defaultVersion(self):
    return "master"

  def installVersion(self, org, pkg, ver):
    cmds = """cd $GOPATH
mkdir -p src/github.com/%s
cd src/github.com/%s
git clone git@github.com:%s/%s
git checkout %s
""" % (
  org,
  org,
  org, pkg,
  ver
)
    print cmds

class BitBucketRepo(object):
  def defaultVersion(self):
    return "trunk"

  def installVersion(self, org, pkg, ver):
    cmds = """cd $GOPATH
mkdir -p src/bitbucket.org/%s
cd src/bitbucket.org/%s
hg clone https://bitbucket.org/%s/%s
hg checkout %s
""" % (
  org,
  org,
  org, pkg,
  ver
)
    print cmds


_REPOS = {
  "github.com": GitHubRepo(),
  "bitbucket.org": BitBucketRepo(),
}

class StateMachine(object):
  def __init__(self):
    self.setRepo("github.com")

  def setRepo(self, r):
    self.repo = _REPOS[r]
    self.org = None
    self.version = self.repo.defaultVersion()

  def setOrg(self, o):
    self.org = o

  def setVersion(self, v):
    self.version = v

  def installPackage(self, p):
    self.repo.installVersion(self.org, p, self.version)
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

