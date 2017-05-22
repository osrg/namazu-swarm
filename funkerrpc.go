package nmzswarm

// Workload is the type for the workload.
// ID is a unique string, typically the shell command itself.
type Workload struct {
	ID string `json:"id"`
}

// ChunkRequest is the type used for funker RPC request
type ChunkRequest struct {
	ChunkID   int        `json:"chunk_id"`
	Workloads []Workload `json:"workloads"`
}

// ChunkResult is the type used for funker RPC result
type ChunkResult struct {
	ChunkID    int    `json:"chunk_id"`
	Successful bool   `json:"successful"`
	RawLog     string `json:"raw_log"`
}
