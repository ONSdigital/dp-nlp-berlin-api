# dp-nlp-berlin-api

A Python microservice to wrap the Berlin package for identifying locations and tagging them with UN-LOCODEs and
ISO-3166-2 subdivisions.

## Setup

It is recommended that you use [Pyenv](https://github.com/pyenv/pyenv) to manage your Python installations.

### Configuration

| Environment variable         | Default               | Description
| ---------------------------- | ---------             | -----------
| FLASK_APP                    | `app/main.py`         | The data files with the areas      
| BERLIN_API_PORT              |  28900                | The port to bind to
| BERLIN_API_HOST              | `0.0.0.0`             | The host to bind to
| BERLIN_API_DATA_LOCATION     | "data/"               | Data location
| BERLIN_API_LOGGING_NAMESPACE | "dp_nlp_berlin_api"   | Logging namespace
| BERLIN_API_GIT_COMMIT        | "000000"              | Git commit 
| BERLIN_API_VERSION           | "0.1.0"               | version

### Install Poetry
```
curl -sSL https://install.python-poetry.org | python3 - 
poetry install
```

## Running

To run the app:

```
make run
```

## Testing

By default, all schemas in the `tests/schemas/valid` directory will be evaluated as part of the unit tests.
Any errors in these schemas will cause a failure.

To run the app's unit tests:

```
make test
```

To test the apps functionality:
```
make run
```

Then, in another terminal window/tab, navigate to a checked out copy of ONS/eq-survey-runner:

```
make test
```

## Usage

This will make an API available on port 28900. It serves simple requests of the
form:

```shell
curl 'http://localhost:28900/v1/berlin/search?q=house+prices+in+londo&state=gb' | jq
```

replacing `localhost` with the local endpoint (`jq` used for formatting).

This will return results of the form:

```json
{
  "matches": [
    {
      "encoding": "UN-LOCODE",
      "id": "ca:lod",
      "key": "UN-LOCODE-ca:lod",
      "words": [
        "london"
      ]
    },
    {
      "encoding": "UN-LOCODE",
      "id": "us:ldn",
      "key": "UN-LOCODE-us:ldn",
      "words": [
        "london"
      ]
    }
    ...
  ]
}
```


## Description

Berlin is a location search engine which  works on an in-memory collection of
all UN Locodes, subdivisions and states (countries). Here are the main
architectural highlights: On startup Berlin does a basic linguistic analysis of
the locations: split names into words, remove diacritics, transliterate
non-ASCII symbols to ASCII. For example,  this allows us to find  “Las Vegas”
when searching for “vegas”.  It employs string interning in order to both
optimise memory usage and allow direct lookups for exact matches. If we can
resolve (parts of) the search term to an existing interned string, it means
that we have a location with this name in the database.

When the user submits the search term, Berlin first does a preliminary analysis
of the search term: 1) split into words and pairs of words 2) try to identify
the former as existing locations (can be resolved to existing interned strings)
and tag them as “exact matches”. This creates many search terms from the
original phrase.  Pre-filtering step. Here we do three things 1) resolve exact
matches by direct lookup in the names and codes tables 2) do a prefix search
via a finite-state transducer 3) do a fuzzy search via a Levenshtein distance
enabled finite-state transducer.  The pre-filtered results are passed through a
string-similarity evaluation algorithm and sorted by score. The results below a
threshold are truncated.  A graph is built from the locations found during the
previous  step in order to link them together hierarchically if possible. This
further boosts some locations. For example, if the user searches for “new york
UK” it will boost the location in Lincolnshire and it will show up higher than
New York city in the USA.  It is also possible to request search only in a
specific country (which is enabled by default for the UK)

Berlin is able to find locations with a high degree of semantic accuracy. Speed
is roughly equal to 10-15 ms per every non-matching word (or typo) + 1 ms for
every exact match. A complex query of 8 words usually takes less than 100 ms
and all of the realistic queries in our test suite take less than 50 ms, while
the median is under 30 ms. Short queries containing  an exact match (case
insensitive) are faster than 10 ms.

The architecture would allow to easily implement as-you-type search suggestions
in under 10 milliseconds if deemed desirable.


### License

Prepared by Flax & Teal Limited for ONS Digital (see LICENSE).
This API is based on [eq-questionnaire-validator](https://github.com/ONSdigital/eq-questionnaire-validator), a tool
from ONS Digital.
