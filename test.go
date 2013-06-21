package foo

import (
	"testing"
)

type pair struct {
	a, b int
}

func TestMustAdd(t *testing.T) {
	exercises := map[int]pair{
		10: pair{5, 5},
		11: pair{3, 8},
		12: pair{10, 2},
	}

	for sum, addends := range exercises {
		s := Sum(addends.a, addends.b)
		if sum != s {
			t.Errorf("Expected %d + %d = %d, got %d", addends.a, addends.b, sum, s)
		}
	}
}
