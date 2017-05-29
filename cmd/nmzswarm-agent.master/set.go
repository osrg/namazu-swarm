package main

import (
	"math"
	"math/rand"
)

// chunkStrings chunks the string slice
func chunkStrings(x []string, numChunks int) [][]string {
	var result [][]string
	if numChunks > len(x) {
		numChunks = len(x)
	}
	i := 0
	for len(result) < numChunks {
		chunkSize := int(math.Floor(float64(len(x)-i) / float64(numChunks-len(result))))
		ub := i + chunkSize
		result = append(result, x[i:ub])
		i += chunkSize
	}
	return result
}

// shuffleStrings shuffles strings
func shuffleStrings(x []string, seed int64) {
	r := rand.New(rand.NewSource(seed))
	for i := range x {
		j := r.Intn(i + 1)
		x[i], x[j] = x[j], x[i]
	}
}
