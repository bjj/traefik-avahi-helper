# traefik-avahi-helper

A helper container to expose proxied containers as mDNS CNAMEs
or A records that are being proxied by the offical Traefik docker container.

It reads the same container labels as the Traefik container:

```
traefik.http.routers.r1.rule=Host(`myservice.local`)
```

This will create a CNAME or A record for `myservice.local` depending on your configuration.

## Installing

`docker pull hardillb/traefik-avahi-helper`

Currently there are AMD64 and ARM64 based builds.

## Running

Choose to use CNAMEs or A records. The main difference is that Windows only supports A records.

To work this needs the following 2 volumes mounted:

` -v /var/run/docker.sock:/var/run/docker.sock`

This allows the container to monitor docker

` -v /run/dbus/system_bus_socket:/run/dbus/system_bus_socket`

And this allows the container to send dbus commands to the host OS's Avahi daemon

```
$ docker run -d -v /var/run/docker.sock:/var/run/docker.sock -v /run/dbus/system_bus_socket:/run/dbus/system_bus_socket githubbjj/traefik-avahi-helper 
```

## Use A Records for Windows Compatibility

Pass `-e TRAEFIK_AVAHI_HELPER_DNS_TYPE=A --network=host` to set the environment variable to use A records instead of the default CNAME records. Host mode is required so that the container can enumerate the real network interfaces.

## AppArmor

If you are running on system with AppArmor installed you may get errors about not being able to send d-bus messages. To fix this add
`--privileged` to the command line.

This is a temp workaround until I can work out a suitable policy to apply.

## Acknowledgement

This uses and borrows heavily from [mdns-publisher](https://github.com/alticelabs/mdns-publisher)
