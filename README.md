# DEPRECATED

Negativo has signal-desktop shipping with his multimedia repos.


https://negativo17.org/

the signal-desktop sources used there can be found at

https://github.com/negativo17/Signal-Desktop

.

Since the spec file has various issues, and the one linked above is shorter and more readable.

## CI pipeline for Signal-Desktop fedora rpm

See [ci.spearow.io](https://ci.spearow.io/teams/main/pipelines/signal-desktop) for the current status or a build history.

## Known Issues

With the recent issues building, this requires the following packages and modules:

```
yarn
nodejs:12
node-gyp
```

unfortunately rpm spec files do not support modules just yet, so one has to make sure the right version is installed beforehands!

## rpm

The repository is located on the fedora provided rpm infrastructure as a service.

* [copr repository](http://copr-fe.cloud.fedoraproject.org/coprs/drahnr/signal-desktop)

### Bugs

Please file bugs regarding the APP itself to signal itself, bugs regarding packaging or CI are very welcome.
