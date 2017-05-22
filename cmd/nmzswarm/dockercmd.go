package main

import (
	"os"
	"os/exec"

	"github.com/docker/docker/client"
)

func system(commands [][]string) error {
	for _, c := range commands {
		cmd := exec.Command(c[0], c[1:]...)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.Env = os.Environ()
		if err := cmd.Run(); err != nil {
			return err
		}
	}
	return nil
}

func pushImage(unusedCli *client.Client, remote string) error {
	// FIXME: eliminate os/exec (but it is hard to pass auth without os/exec ...)
	return system([][]string{
		{"docker", "image", "push", remote},
	})
}

func deployStack(unusedCli *client.Client, stackName, composeFilePath string) error {
	// FIXME: eliminate os/exec (but stack is implemented in CLI ...)
	return system([][]string{
		{"docker", "stack", "deploy",
			"--compose-file", composeFilePath,
			"--with-registry-auth",
			stackName},
	})
}
