# Client for interacting with the captest.io application programming interface 

This repository maintains two python programs: `cap_client.py` and `cap_admin_client.py`. The first is a client for managing assignments. The second program is intended for managing other content on the platform (currently restricted to admin users).


## Installation

The client relies on python (3.7+), but does not otherwise require any special installation steps. You can just clone the repository and start using the client straight away.

For a basic check that the software works, execute `cap_client.py` with the `--help` option.

```
python cap_client.py --help
```

This should display a message listing all the available command-line arguments along with brief descriptions.


## Credentials

Most interactions with the application programming interface (API) require authentification with a username and an access token. This information can be provided through the `--username` and `--token` arguments on the command line. However, these credentials can also be provided in a file, avoiding repeating these data in each command. 

To use file-based credentials, create a file `secrets.yaml` with yaml-formatted content as follows:

```
testuser:
  token: Abcdefghijklmnopqrstuvwxyz1234
```

In your file, replace `testuser` with your own username, and change the value `Abcdefghijklmnopqrstuvwxyz1234` to the token provided to you on the www.captest.io website (Profile > Settings > Tokens).


## Managing assignments

Managing assignments is handled by the `cap_client.py` program. Commands with this
program typically take the following form

```
python cap_client.py [action] [arguments]
```

Here `action` is a verb-string, e.g. `start` or `list_assignments`. The `arguments` are a series of key-value pairs (see examples below). Upon execution, all commands print JSON-formatted results to the terminal.

To obtain a list of assignments,

```
python cap_client.py list_assignments
```

This will display a JSON array. For a new user, the output will be `[]` (an empty JSON array). Otherwise, the output can be quite long.

To start a new assignment, specify a challenge unique universal identifier using `--uuid`, or a combination of challenge name and version using `--name` and `--version`. For example, to start an assignment for the trivial challenge used in the tutorial, use the following command,

```
python cap_client.py start --name trivial --version 0.1
```

This will return a JSON object. The field `uuid` will hold a unique identifier for the assignment. Subsequent commands will require providing this uuid on the command line. The snippets below use `[uuid]` as a placeholder, but this should be replaced by an actual uuid string.

To view the status of the assignment,

```
python cap_client.py view --uuid [uuid]
```

When the status of the assignment changes to `generated`, it is possible to download the assignment data files. 

```
python cap_client.py download --uuid [uuid]
```

The command will display a summary of the downloaded files in the terminal. The data files will appear in the current working directory. 

To upload a response file,

```
python cap_client.py upload_response --uuid [uuid] --file [response-file]
```

(The string `[response-file]` is a placeholder; it should be replaced by a path to an actual data file). The output will summarize a new uuid for the uploaded file. If the response file is uploaded in error, it can be removed using action `remove_response` and specifying the assignment uuid.  

To submit an assignment for evaluation,

```
python cap_client.py submit --uuid [uuid]
```

After submitting the assignment, it is a good idea to check its status.

```
python cap_client.py view --uuid [uuid]
```

The status of the assignment should change from `generated` to `submitted` and later to `complete`.


## Admin tools

The admin tools work similarly as the assignment-management tools. However,
the API endpoints are currently restricted to admin users only.


## Comments, questions, suggestions, bugs?

Please raise an issue in the github repository. 

