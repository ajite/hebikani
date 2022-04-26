WaniKani CLI
============


This is an alpha release, and it is not working yet.

INSTALL
-------

In a new python environment.

```
python setup.py develop
```

RUN
---

Check the help:
```
python wanikani.py --help
```

To display your review summary:
```
python wanikani.py summary
````

To start a review session:
```
python wanikani.py reviews
```



TODO
----

- Submit reviews to the API
- Link cards for the same "subject" together.
- Change the INPUT system to convert alphabetical characters to hiragana or katana. So far it works by using a Japanese input only.
- Improve the CLI display.