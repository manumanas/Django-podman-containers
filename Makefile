build:
	podman build -t ubuntu-systemd ./ubuntu_systemd
	podman build -t headscale-server ./headscale

run:
	podman run -d \
	--name headscale \
	-p 8080:8080 \
	headscale-server

stop:
	podman stop headscale || true
	podman rm headscale || true

clean:
	podman rmi ubuntu-systemd || true
	podman rmi headscale-server || true