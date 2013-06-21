package foo

import (
  t1 "github.com/sam-falvo/test-repo-1"
  _ "github.com/sam-falvo/test-repo-2"
  t3 "github.com/sam-falvo/test-repo-3"
)

func Sum(a, b int) int {
  t1.Hello()
  t3.Goodbye()
	return a + b
}
