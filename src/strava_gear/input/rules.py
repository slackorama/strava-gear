import datetime
from itertools import chain
from typing import Dict
from typing import Iterable
from typing import Iterator

import jsonschema  # type: ignore [import]
import yaml

from ..data import BikeId
from ..data import BikeName
from ..data import Component
from ..data import ComponentId
from ..data import ComponentName
from ..data import Meters
from ..data import Rule
from ..data import Rules
from ..data import Seconds
from .date import parse_datetime

config_format_checker = jsonschema.FormatChecker()
config_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'aliases': {
            'type': 'object',
            'additionalProperties': {'type': 'string'},
        },
        'components': {
            'type': 'object',
            'additionalProperties': {
                'oneOf': [
                    {'type': 'null'},
                    {'type': 'string'},
                    {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'name': {'type': 'string'},
                            'kms': {'type': 'number'},
                            'hours': {'type': 'number'},
                        },
                    },
                ],
            }
        },
        'rules': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'since': {'format': 'datetime'},
                },
                'additionalProperties': {
                    'type': 'object',
                    'additionalProperties': {
                        'oneOf': [
                            {'type': 'null'},
                            {'type': 'string'},
                        ],
                    },
                },
            },
        },
    },
}


@config_format_checker.checks('datetime')
def format_checker_datetime(d):
    return isinstance(d, (datetime.datetime, datetime.date,))


def process_component(k: str, v) -> Component:
    if v is None:
        return Component(ident=ComponentId(k), name=ComponentName(k))
    elif isinstance(v, str):
        return Component(ident=ComponentId(k), name=ComponentName(v))
    else:
        return Component(
            ident=ComponentId(k),
            name=ComponentName(v.get('name', k)),
            distance=Meters(v.get('kms', 0) * 1000.0),
            time=Seconds(v.get('hours', 0) * 3600.0))


def undeclared_components(rules: Iterable[Rule], components: Iterable[Component]) -> Iterator[Component]:
    component_ids = {c.ident for c in components}
    for r in rules:
        for m in chain(r.bikes.values(), r.hashtags.values()):
            for c in m.values():
                if c is not None and c not in component_ids:
                    yield Component(ident=ComponentId(c), name=ComponentName(c))


def process_rule(r: Dict, aliases: Dict[BikeName, BikeId]) -> Rule:
    bikes = {}
    hashtags = {}
    kwargs = {}
    for k, v in r.items():
        if k == 'since':
            d = parse_datetime(v)
            assert d is not None
            kwargs[k] = d
        elif k.startswith('#'):
            hashtags[k] = v
        else:
            bikes[aliases.get(k, k)] = v

    return Rule(bikes=bikes, hashtags=hashtags, **kwargs)


def process_rules(c: Dict, aliases: Dict[BikeName, BikeId]) -> Rules:
    aliases = {**aliases, **c.get('aliases', {})}
    components = [process_component(k, v) for k, v in c.get('components', {}).items()]
    rules = [process_rule(r, aliases=aliases) for r in c.get('rules', [])]

    components.extend(undeclared_components(rules, components))

    return Rules(
        bike_names={v: k for k, v in aliases.items()},
        components=components,
        rules=rules,
    )


def read_rules(inp, aliases: Dict[BikeName, BikeId] = {}) -> Rules:
    c = yaml.safe_load(inp)
    jsonschema.validate(c, config_schema, format_checker=config_format_checker)
    return process_rules(c, aliases)