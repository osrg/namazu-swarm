package main

import (
	"fmt"
	"reflect"
	"testing"
	"time"
)

func generateInput(inputLen int) []string {
	input := []string{}
	for i := 0; i < inputLen; i++ {
		input = append(input, fmt.Sprintf("s%d", i))
	}

	return input
}

func testChunkStrings(t *testing.T, inputLen, numChunks, expectedResultNumChunks int) [][]string {
	t.Logf("inputLen=%d, numChunks=%d", inputLen, numChunks)
	input := generateInput(inputLen)
	result := chunkStrings(input, numChunks)
	t.Logf("result has %d chunks", len(result))
	if expectedResultNumChunks != len(result) {
		t.Fatalf("expected %d, got %d", expectedResultNumChunks, len(result))
	}
	inputReconstructedFromResult := []string{}
	for i, chunk := range result {
		t.Logf("chunk %d has %d elements", i, len(chunk))
		inputReconstructedFromResult = append(inputReconstructedFromResult, chunk...)
	}
	if !reflect.DeepEqual(input, inputReconstructedFromResult) {
		t.Fatal("input != inputReconstructedFromResult")
	}
	return result
}

func TestChunkStrings_4_4(t *testing.T) {
	testChunkStrings(t, 4, 4, 4)
}

func TestChunkStrings_4_1(t *testing.T) {

	testChunkStrings(t, 4, 1, 1)
}

func TestChunkStrings_1_4(t *testing.T) {
	testChunkStrings(t, 1, 4, 1)
}

func TestChunkStrings_1000_8(t *testing.T) {
	testChunkStrings(t, 1000, 8, 8)
}

func TestChunkStrings_1000_9(t *testing.T) {
	testChunkStrings(t, 1000, 9, 9)
}

func TestChunkStrings_4_3(t *testing.T) {
	testChunkStrings(t, 4, 3, 3)
}

func TestChunkStrings_200_180(t *testing.T) {
	testChunkStrings(t, 200, 180, 180)
}

func testShuffleStrings(t *testing.T, inputLen int, seed int64) {
	t.Logf("inputLen=%d, seed=%d", inputLen, seed)
	x := generateInput(inputLen)
	shuffleStrings(x, seed)
	t.Logf("shuffled: %v", x)
}

func TestShuffleStrings_100(t *testing.T) {
	testShuffleStrings(t, 100, time.Now().UnixNano())
}
