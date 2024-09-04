# Document Summarizer ![](https://github.com/ains-arch/docsum/workflows/tests/badge.svg)

`docsum.py` takes a file (of any type) as a command line argument and
summarizes that file using the Groq API.

## Getting started

To install the required Python packages for this project, you can use the
`requirements.txt` file included in this repository.

Clone the repository.

```
$ git clone https://github.com/ains-arch/docsum.git
$ cd docsum
```

Create a python virtual environment for packages (optional but recommended).
```
$ python3 -m venv venv
$ . ./venv/bin/activate
```

Install packages.
```
$ pip3 install -r requirements.txt
```

You'll need an API key from [Groq](https://groq.com).

Add the API key to `.env` and register it.
```
$ vim .env
$ export $(cat .env)
```

## Usage

Pass a file path to `docsum.py` from the command line. For example:
```
$ python3 docsum.py docs/declaration.txt
```

If you want to try a prompt injection, use the `.attack` file:
```
$ python3 docsum.py docs/declaration.txt.attack
```
