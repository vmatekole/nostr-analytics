#!/bin/sh

set -e

# activate our virtual environment here
. .venv/bin/activate

# You can put other setup logic here

# Evaluating passed command:


command=$1

# Evaluate the command
case $command in
    "produce-events")
        python orchestration/prefect/elt_pipeline.py stream-events -k 1,7,30023 -r wss://relay.damus.io,wss://nostr.wine
        ;;
    "process-events")
        python orchestration/prefect/elt_pipeline.py process-events
        ;;
    "produce-relays")
        python orchestration/prefect/elt_pipeline.py stream-relays -r wss://relay.damus.io,wss://nostr.wine
        ;;
    "process-relays")
        python orchestration/prefect/elt_pipeline.py process-relays
        ;;
    *)
        echo "Invalid command. Please specify 'stream-events', 'process-events', 'stream-relays', 'process-relays',."
        exit 1
        ;;
esac
