package main

import (
	"bytes"
	"io"
	"log"
	"os"
	"os/exec"
	"time"

	nmzswarm "github.com/osrg/namazu-swarm"
)

func exek(executor string, req nmzswarm.ChunkRequest) nmzswarm.ChunkResult {
	var (
		in  bytes.Buffer
		out bytes.Buffer
	)
	for _, workload := range req.Workloads {
		log.Printf("Chunk %d: workload: %+v", req.ChunkID, workload)
		in.Write([]byte(workload.ID + "\n"))
	}
	cmd := exec.Command("/bin/sh", "-c", executor)
	cmd.Env = os.Environ()
	cmd.Stdin = &in
	cmd.Stdout = io.MultiWriter(&out, os.Stdout)
	cmd.Stderr = io.MultiWriter(&out, os.Stderr)
	begin := time.Now()
	log.Printf("Chunk %d: executing with %q", req.ChunkID, executor)
	err := cmd.Run()
	elapsed := time.Now().Sub(begin)
	if err != nil {
		log.Printf("Chunk %d: got err=%v, elapsed=%v", req.ChunkID, err, elapsed)
	} else {
		log.Printf("Chunk %d: successful, elapsed=%v", req.ChunkID, elapsed)
	}
	return nmzswarm.ChunkResult{
		ChunkID:    req.ChunkID,
		Successful: err == nil,
		RawLog:     out.String(),
	}
}
