package main

import (
	"errors"
	"flag"
	"io/ioutil"
	"log"
	"strings"
)

func main() {
	if err := xmain(); err != nil {
		log.Fatalf("fatal error: %v", err)
	}
}

func xmain() error {
	workerService := flag.String("worker-service", "", "Name of worker service")
	chunks := flag.Int("chunks", 0, "Number of chunks")
	input := flag.String("input", "", "Path to input file")
	randSeed := flag.Int64("rand-seed", int64(0), "Random seed")
	shuffle := flag.Bool("shuffle", false, "Shuffle the input so as to mitigate makespan nonuniformity")
	flag.Parse()
	if *workerService == "" {
		return errors.New("worker-service unset")
	}
	if *chunks == 0 {
		return errors.New("chunks unset")
	}
	if *input == "" {
		return errors.New("input unset")
	}

	workloads, err := loadWorkloads(*input)
	if err != nil {
		return err
	}
	workloadChunks := chunkWorkloads(workloads, *chunks, *shuffle, *randSeed)
	log.Printf("Loaded %d workloads (%d chunks)", len(workloads), len(workloadChunks))
	return executeWorkloads(*workerService, workloadChunks)
}

func chunkWorkloads(workloads []string, numChunks int, shuffle bool, randSeed int64) [][]string {
	// shuffling (experimental) mitigates makespan nonuniformity
	// Not sure this can cause some locality problem..
	if shuffle {
		shuffleStrings(workloads, randSeed)
	}
	return chunkStrings(workloads, numChunks)
}

func loadWorkloads(filename string) ([]string, error) {
	b, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	var workloads []string
	for _, line := range strings.Split(string(b), "\n") {
		s := strings.TrimSpace(line)
		if s != "" {
			workloads = append(workloads, s)
		}
	}
	return workloads, nil
}
