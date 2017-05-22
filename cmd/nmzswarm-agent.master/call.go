package main

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/bfirsh/funker-go"
	nmzswarm "github.com/osrg/namazu-swarm"
)

const (
	// funkerRetryTimeout is for the issue https://github.com/bfirsh/funker/issues/3
	// When all the funker replicas are busy in their own job, we cannot connect to funker.
	funkerRetryTimeout  = 1 * time.Hour
	funkerRetryDuration = 1 * time.Second
)

// ticker is needed for some CI (e.g., on Travis, job is aborted when no output emitted for 10 minutes)
func ticker(d time.Duration) chan struct{} {
	t := time.NewTicker(d)
	stop := make(chan struct{})
	go func() {
		for {
			select {
			case <-t.C:
				log.Printf("tick (just for keeping CI job active) per %s", d.String())
			case <-stop:
				t.Stop()
			}
		}
	}()
	return stop
}

func executeWorkloads(funkerName string, workloadChunks [][]string) error {
	tickerStopper := ticker(9*time.Minute + 55*time.Second)
	defer func() {
		close(tickerStopper)
	}()
	begin := time.Now()
	log.Printf("Executing %d chunks in parallel, against %q", len(workloadChunks), funkerName)
	var wg sync.WaitGroup
	var passed, failed uint32
	for chunkID, workloads := range workloadChunks {
		log.Printf("Executing chunk %d (contains %d workload filters)", chunkID, len(workloads))
		wg.Add(1)
		go func(chunkID int, workloadStrings []string) {
			defer wg.Done()
			chunkBegin := time.Now()
			var workloads []nmzswarm.Workload
			for _, x := range workloadStrings {
				workloads = append(workloads, nmzswarm.Workload{ID: x})
			}
			result, err := executeWorkloadChunkWithRetry(funkerName, nmzswarm.ChunkRequest{
				ChunkID:   chunkID,
				Workloads: workloads,
			})
			if result.RawLog != "" {
				for _, s := range strings.Split(result.RawLog, "\n") {
					log.Printf("Log (chunk %d): %s", chunkID, s)
				}
			}
			if err != nil {
				log.Printf("Error while executing chunk %d: %v",
					chunkID, err)
				atomic.AddUint32(&failed, 1)
			} else {
				if result.Successful {
					atomic.AddUint32(&passed, 1)
				} else {
					atomic.AddUint32(&failed, 1)
				}
				log.Printf("Finished chunk %d [%d/%d] with %d workload filters in %s, successful=%v.",
					chunkID, passed+failed, len(workloadChunks), len(workloads),
					time.Now().Sub(chunkBegin), result.Successful)
			}
		}(chunkID, workloads)
	}
	wg.Wait()
	// TODO: print actual number of successful workloads rather than chunks
	log.Printf("Executed %d chunks in %s. PASS: %d, FAIL: %d.",
		len(workloadChunks), time.Now().Sub(begin), passed, failed)
	if failed > 0 {
		return fmt.Errorf("%d chunks failed", failed)
	}
	return nil
}

func executeWorkloadChunk(funkerName string, req nmzswarm.ChunkRequest) (nmzswarm.ChunkResult, error) {
	ret, err := funker.Call(funkerName, req)
	if err != nil {
		return nmzswarm.ChunkResult{}, err
	}
	tmp, err := json.Marshal(ret)
	if err != nil {
		return nmzswarm.ChunkResult{}, err
	}
	var result nmzswarm.ChunkResult
	err = json.Unmarshal(tmp, &result)
	return result, err
}

func executeWorkloadChunkWithRetry(funkerName string, req nmzswarm.ChunkRequest) (nmzswarm.ChunkResult, error) {
	timeout, tick := time.After(funkerRetryTimeout), time.Tick(funkerRetryDuration)
	i := 0
	for {
		select {
		case <-timeout:
			return nmzswarm.ChunkResult{}, fmt.Errorf("could not call executeWorkloadChunk(%q, %d) in %v", funkerName, req.ChunkID, funkerRetryTimeout)
		case <-tick:
			result, err := executeWorkloadChunk(funkerName, req)
			if err == nil {
				log.Printf("executeWorkloadChunk(%q, %d) returned successful=%v in trial %d", funkerName, req.ChunkID, result.Successful, i)
				return result, nil
			}
			if errorSeemsInteresting(err) {
				log.Printf("Error while calling executeWorkloadChunk(%q, %d), will retry (trial %d): %v",
					funkerName, req.ChunkID, i, err)
			}
		}
		i++
	}
}

//  errorSeemsInteresting returns true if err does not seem about https://github.com/bfirsh/funker/issues/3
func errorSeemsInteresting(err error) bool {
	boringSubstrs := []string{"connection refused", "connection reset by peer", "no such host", "transport endpoint is not connected", "no route to host"}
	errS := err.Error()
	for _, boringS := range boringSubstrs {
		if strings.Contains(errS, boringS) {
			return false
		}
	}
	return true
}
