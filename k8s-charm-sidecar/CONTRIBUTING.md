# juju-dashboard

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Code overview


## Intended use case

This charm is meant to implement the Juju Dashboard. It is distributed
along with Juju, and installed automagically.


## Roadmap


## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
