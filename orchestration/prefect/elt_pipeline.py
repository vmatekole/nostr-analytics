from pydoc import cli

import click
from google.cloud import bigquery
from prefect import Flow, flow, task

from base.config import ConfigSettings
from kafka.consumer import NostrConsumer
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, RelayTopic
from nostr.event import EventKind

#  Tasks


@task(name='Discover Relays', log_prints=True)  # type: ignore
def extract_relays(relay_urls: list[str]):
    relay_nostr_producer: NostrProducer = NostrProducer(
        ConfigSettings.relay_kafka_topic, RelayTopic
    )
    relay_nostr_producer.stream_relays(relay_urls=relay_urls)


@task(name='Process Nostr Relays', log_prints=True)  # type: ignore
def load_relays():
    relay_nostr_consumer: NostrConsumer = NostrConsumer(
        [ConfigSettings.relay_kafka_topic], RelayTopic
    )
    relay_nostr_consumer.consume_relays()


@task(name='Stream Nostr events', log_prints=True)  # type: ignore
def extract_events(kinds: list[EventKind], relay_urls: list[str]):
    event_nostr_producer: NostrProducer = NostrProducer(
        ConfigSettings.event_kafka_topic, EventTopic
    )
    event_nostr_producer.stream_events(kinds=kinds, relay_urls=relay_urls)


@task(name='Process Nostr Event Stream', log_prints=True)  # type: ignore
def load_events():
    event_nostr_consumer: NostrConsumer = NostrConsumer(
        [ConfigSettings.event_kafka_topic], EventTopic
    )
    event_nostr_consumer.consume_events()


# End of tasks


@click.group()
def cli():
    pass


def _split_and_strip(ctx, opts: click.Option, v: str):
    return [s.strip() for s in v.split(',')]


@cli.command()
@click.option(
    '--relays',
    '-r',
    callback=_split_and_strip,
    help='Specify relays separated by commas.',
)
@flow(name='Nostr Relays Stream')  # type: ignore
def stream_relays(relays: list[str]):
    extract_relays(relays)


@cli.command()
@flow(name='Process Nostr Relays Stream')  # type: ignore
def process_relays():
    load_relays()


@cli.command()
@click.option(
    '--kinds',
    '-k',
    callback=_split_and_strip,
    help='Specify kinds separated by commas.',
)
@click.option(
    '--relays',
    '-r',
    callback=_split_and_strip,
    help='Specify relays separated by commas.',
)
@flow(name='Nostr Events Stream')  # type: ignore
def stream_events(kinds: list[EventKind], relays: list[str]):
    extract_events(kinds, relays)


@cli.command()
@flow(name='Process Nostr Events Stream')  # type: ignore
def process_events():
    load_events()


if __name__ == '__main__':
    cli()
