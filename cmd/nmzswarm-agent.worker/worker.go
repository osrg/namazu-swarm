package main

import (
	"errors"
	"flag"
	"log"

	"github.com/bfirsh/funker-go"
	nmzswarm "github.com/osrg/namazu-swarm"
)

func main() {
	if err := xmain(); err != nil {
		log.Fatalf("fatal error: %v", err)
	}
}

func xmain() error {
	executor := flag.String("executor", "", "executor scripts (receives workload IDs via stdin)")
	flag.Parse()
	if *executor == "" {
		return errors.New("executor unset")
	}
	return handle(*executor)
}

func handle(executor string) error {
	log.Printf("Waiting for a funker request")
	return funker.Handle(func(req *nmzswarm.ChunkRequest) nmzswarm.ChunkResult {
		return exek(executor, *req)
	})
}
