# cap_client

Command-line client for interacting with the CAPtest API.


## Setup and general options

### API URL

The base url for the API can be set using `--api`. This has a default value, so it only needs to be set if the API requests are intended for a non-standard instance of the service.


### Credentials

Most commands sent to the API require authorization. This is achieved by sending a username and an access token alongside each API request. 

To provide authorization on the command line, use the `--username` and `--token` arguments. The access token can be copied from the web interface. **An access 
token is not the same as a user password**.

It is also possible to set an access token in a configuration file with secret information. The location of the secrets file can be specified via argument `--secrets`, the default file is `secrets.yaml`. When an access token is not provided on the command line with `--token`, a value is extracted from the secrets file. Most examples below omit writing the access token. 

### Logging

By default, the client displays only outputs json objects summarizing one or more responses from the API, or logs error messages. Activating the `--verbose` flag makes the client emit more information, including details about each API request sent to the server.


## Managing assignments




## Managing documents

Documents correspond to the text-based pages on the website. There are several types of documents: `blog`, `documentation`, `resource`, `challenge`. Managing these documents requires an account with admin privileges on the server. The examples below use the `admin` and assume that its access token is provided in the secrets file. 

Document definitions must be provided in text files with a header and markdown content. 

```
---
name: document-name
version: 1.0
title: Document Name
tags: tag_1 tag_2
datafile: primary_file.extension
support:
  - file_1.webp
  - file_2.webp
---

Content of document in *markdown* format ...
```


### Creating new documents

To create a new document, e.g. a blog post,

```
python cap_client.py create \
  --username admin --collection blog --file filename.md
```

This action creates a new database record on the server. A new document is not public and is not published, so it does not automatically appear in any lists on the website.


### Uploading document-associated files

Some documents rely on auxiliary files. 

Documents of type `resource` and `challenge` must be associated to a primary datafile, e.g. an object with external data or a challenge configuration, respectively. The location of this file can be specified via `datafile` in the file header. This can be uploaded using `upload_primary`.

```
python cap_client.py upload_primary \
  --username admin --collection blog --file filename.md
```

Other files can also be uploaded as support files, for example to include images as part of the document description. A list of support files can be specified via `support` in the file header, and the files can be uploaded using `upload_support`.

```
python cap_client.py upload_support \
  --username admin --collection blog --file filename.md
```


### Publishing documents

To make a new document visible to the public, or to update an already existing document, use the `publish` command.

```
python cap_client.py publish \
  --username admin --collection blog --file filename.md
```

'Publishing' a document means that it becomes available on the website. A 'published' document can still be changed/updated - just repeat the publishing command with a new markdown file. 


### Marking documents as obsolete

To mark a document as obsolete (and hide it from view in standard listings), use the `obsolete` command.

```
python cap_client.py obsolete \
  --username admin --collection blog --file filename.md
```



### Shortcuts

Document-management commands can be performed in batch by specifying a directory instead of file name. For example, it is possible to 'publish', i.e. to update the content of all documents saved in one directory.

```
python cap_client.py publish \
  --username admin --collection blog --dir blog/ 
```

