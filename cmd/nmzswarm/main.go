package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"strings"
	"time"

	"github.com/Sirupsen/logrus"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"

	"github.com/osrg/namazu-swarm"
)

func main() {
	if err := xmain(); err != nil {
		logrus.Fatalf("fatal error: %v", err)
	}
}

// xmain can call os.Exit()
func xmain() error {
	// Should we use cobra maybe?
	orchestrator := flag.String("orchestrator", "docker", "orchestrator")
	stack := flag.String("docker-stack", "nmzswarm", "Docker stack name (for docker orchestrator)")
	source := flag.String("source", "", "The source image name. Required always.")
	target := flag.String("target", "", "If empty, random name may be automatically generated. Required for -push.")
	push := flag.Bool("push", false, "Push the image to the registry. Required for distribuetd execution.")
	replicas := flag.Int("replicas", 1, "Number of worker service replica")
	chunks := flag.Int("chunks", 0, "Number of test chunks executed in batch (0 == replicas)")
	flag.Parse()
	if *orchestrator != "docker" {
		return fmt.Errorf("unsupported orchestrator: %q", *orchestrator)
	}
	if *stack == "" {
		return errors.New("-stack needs to be specified")
	}
	if *source == "" {
		return errors.New("-source needs to be specified")
	}
	if *target == "" {
		if *push {
			return errors.New("-target needs to be specified for -push")
		} else {
			*target = strings.Split(*source, ":")[0] + ":nmzswarm-target"
		}
	}
	if *source == *target {
		return errors.New("-target needs to be different from -source")
	}
	if *replicas < 0 {
		return errors.New("bad -replicas")
	}
	if *chunks < 0 {
		return errors.New("bad -chunks")
	}
	if *chunks == 0 {
		*chunks = *replicas
	}
	cli, err := client.NewEnvClient()
	if err != nil {
		return err
	}
	tmp, err := ioutil.TempDir("", "nmzswarm")
	if err != nil {
		return err
	}
	defer os.RemoveAll(tmp)
	logrus.Infof("Injecting Namazu Swarm agents to %q (--> %q)", *source, *target)
	if err := injectImage(cli, tmp, *target, *source); err != nil {
		return err
	}
	if *push {
		logrus.Infof("Pushing %q", *target)
		if err = pushImage(cli, *target); err != nil {
			return err
		}
	}

	rc, err := runDockerOrchestrator(cli, tmp, *stack, *replicas, *chunks, *target)
	if err != nil {
		return err
	}
	logrus.Infof("Exit status: %d", rc)
	os.Exit(int(rc))
	return nil
}

// TODO: implement KubernetesOrchestrator
func runDockerOrchestrator(cli *client.Client, tmp, stack string, replicas, chunks int, target string) (int64, error) {
	targetLabels, err := imageLabels(cli, target)
	if err != nil {
		return 1, err
	}
	workerScript, ok := targetLabels[nmzswarm.ImageLabelV0WorkerScript]
	if !ok {
		return 1, fmt.Errorf("image label %q unset", nmzswarm.ImageLabelV0WorkerScript)
	}
	info, err := cli.Info(context.Background())
	if err != nil {
		return 1, err
	}
	compose, err := createCompose(tmp, composeOptions{
		Replicas:     replicas,
		Chunks:       chunks,
		Image:        target,
		WorkerScript: workerScript,
		SelfNodeID:   info.Swarm.NodeID,
		RandSeed:     time.Now().UnixNano(),
	})
	if err != nil {
		return 1, err
	}
	logrus.Infof("Deploying stack %q", stack)
	defer func() {
		logrus.Infof("NOTE: You may want to inspect or clean up the following resources:")
		logrus.Infof(" - Stack: %s", stack)
		logrus.Infof(" - Target image: %s", target)
	}()
	if err = deployStack(cli, stack, compose); err != nil {
		return 1, err
	}
	logrus.Infof("The log will be displayed here after some duration. "+
		"You can watch the live status via `docker service logs %s_worker`",
		stack)
	masterContainerID, err := waitForMasterUp(cli, stack)
	if err != nil {
		return 1, err
	}
	return waitForContainerCompletion(cli, os.Stdout, os.Stderr, masterContainerID)
}

func imageLabels(cli *client.Client, image string) (map[string]string, error) {
	insp, _, err := cli.ImageInspectWithRaw(context.Background(), image)
	if err != nil {
		return nil, err
	}
	return insp.Config.Labels, nil
}

func waitForMasterUp(cli *client.Client, stackName string) (string, error) {
	timeout, tick := time.After(30*time.Second), time.Tick(1*time.Second)
	for {
		select {
		case <-timeout:
			return "", fmt.Errorf("master not running in stack %s?", stackName)
		case <-tick:
			fil := filters.NewArgs()
			fil.Add("label", "com.docker.stack.namespace="+stackName)
			// FIXME(AkihiroSuda): we should not rely on internal service naming convention
			fil.Add("label", "com.docker.swarm.service.name="+stackName+"_master")
			masters, err := cli.ContainerList(context.Background(), types.ContainerListOptions{
				All:     true,
				Filters: fil,
			})
			if err != nil {
				return "", err
			}
			if len(masters) > 0 {
				return masters[0].ID, nil
			}
		}
	}
}

func waitForContainerCompletion(cli *client.Client, stdout, stderr io.Writer, containerID string) (int64, error) {
	stream, err := cli.ContainerLogs(context.Background(),
		containerID,
		types.ContainerLogsOptions{
			ShowStdout: true,
			ShowStderr: true,
			Follow:     true,
		})
	if err != nil {
		return 1, err
	}
	stdcopy.StdCopy(stdout, stderr, stream)
	stream.Close()
	return cli.ContainerWait(context.Background(), containerID)
}
