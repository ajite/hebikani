# CHANGELOG



## v1.7.2 (2023-10-17)

### Fix

* fix: listen to audio display + ci (#62) ([`14f4bb0`](https://github.com/ajite/hebikani/commit/14f4bb0f9dfe9738beed8523d58013bf7611ce2e))


## v1.7.1 (2023-10-17)

### Fix

* fix: subject without readings (#61) ([`30c891e`](https://github.com/ajite/hebikani/commit/30c891e7f317ff463f604d7674acd8e149efc471))


## v1.7.0 (2023-10-17)

### Ci

* ci: pyproject semantic 8 (#59) ([`901073d`](https://github.com/ajite/hebikani/commit/901073da89b6876fc44fa9862323b1a4e2f19085))

### Feature

* feat: add subject caching, improve question reading system (#60)

User can download subject in cache using hebikani --download
User can use kanji reading on vocabulary, the answers will be set as inexact as opposed to incorrect. ([`0a5b294`](https://github.com/ajite/hebikani/commit/0a5b2949b061fbaaa9e6a6b6d8d98b04a254ac14))


## v1.6.4 (2023-10-05)

### Ci

* ci: build new action to build on pypi (#58) ([`7a5593d`](https://github.com/ajite/hebikani/commit/7a5593dfaa176f27bce9f129ceb6e83e09b4b099))

### Fix

* fix: png for non utf character were returning 403 (#57)

* fix: png for non utf character were returning 403

Used SVG instead

* ci: fix poetry version ([`f25cf8e`](https://github.com/ajite/hebikani/commit/f25cf8e01f6ff21b68814c9ccef9b44a7ebab786))

* fix(deps): bump certifi from 2021.10.8 to 2022.12.7 (#45)

Bumps [certifi](https://github.com/certifi/python-certifi) from 2021.10.8 to 2022.12.7.
- [Release notes](https://github.com/certifi/python-certifi/releases)
- [Commits](https://github.com/certifi/python-certifi/compare/2021.10.08...2022.12.07)

---
updated-dependencies:
- dependency-name: certifi
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`eee9eae`](https://github.com/ajite/hebikani/commit/eee9eaee97fcebd58ebd6e0fe3fdb09ff0f3a04e))

* fix(deps): bump pyobjc from 8.5.1 to 9.0.1 (#46)

Bumps [pyobjc](https://github.com/ronaldoussoren/pyobjc) from 8.5.1 to 9.0.1.
- [Release notes](https://github.com/ronaldoussoren/pyobjc/releases)
- [Changelog](https://github.com/ronaldoussoren/pyobjc/blob/master/docs/changelog.rst)
- [Commits](https://github.com/ronaldoussoren/pyobjc/commits)

---
updated-dependencies:
- dependency-name: pyobjc
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`a1ddc33`](https://github.com/ajite/hebikani/commit/a1ddc334cdd57950865037ac22b5dad45a0c5f86))

* fix(deps): bump pillow from 9.2.0 to 9.4.0 (#47)

Bumps [pillow](https://github.com/python-pillow/Pillow) from 9.2.0 to 9.4.0.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/9.2.0...9.4.0)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`8e66986`](https://github.com/ajite/hebikani/commit/8e66986e51c58a3f931e19f2a9ca4fef090ca388))


## v1.6.3 (2022-10-27)

### Fix

* fix(deps): bump colorama from 0.4.5 to 0.4.6 (#42)

Bumps [colorama](https://github.com/tartley/colorama) from 0.4.5 to 0.4.6.
- [Release notes](https://github.com/tartley/colorama/releases)
- [Changelog](https://github.com/tartley/colorama/blob/master/CHANGELOG.rst)
- [Commits](https://github.com/tartley/colorama/compare/0.4.5...0.4.6)

---
updated-dependencies:
- dependency-name: colorama
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`d090f3a`](https://github.com/ajite/hebikani/commit/d090f3a7540475ae153d9f21c669b88b9cc70f17))


## v1.6.2 (2022-10-11)

### Fix

* fix(deps): bump mutagen from 1.45.1 to 1.46.0 (#41)

Bumps [mutagen](https://github.com/quodlibet/mutagen) from 1.45.1 to 1.46.0.
- [Release notes](https://github.com/quodlibet/mutagen/releases)
- [Changelog](https://github.com/quodlibet/mutagen/blob/master/NEWS)
- [Commits](https://github.com/quodlibet/mutagen/compare/release-1.45.1...release-1.46.0)

---
updated-dependencies:
- dependency-name: mutagen
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`645dc74`](https://github.com/ajite/hebikani/commit/645dc74fc0f5532991f92e352872a00117442022))


## v1.6.1 (2022-10-11)

### Fix

* fix(deps): bump pyobjc from 8.5 to 8.5.1 (#40)

Bumps [pyobjc](https://github.com/ronaldoussoren/pyobjc) from 8.5 to 8.5.1.
- [Release notes](https://github.com/ronaldoussoren/pyobjc/releases)
- [Changelog](https://github.com/ronaldoussoren/pyobjc/blob/v8.5.1/docs/changelog.rst)
- [Commits](https://github.com/ronaldoussoren/pyobjc/compare/v8.5...v8.5.1)

---
updated-dependencies:
- dependency-name: pyobjc
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`4406acf`](https://github.com/ajite/hebikani/commit/4406acf009291a0a7b47202ae5f24c2bf8ec7758))


## v1.6.0 (2022-08-03)

### Build

* build(deps): bump sphinx from 5.1.0 to 5.1.1 (#38)

Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 5.1.0 to 5.1.1.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/5.x/CHANGES)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v5.1.0...v5.1.1)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`6a28344`](https://github.com/ajite/hebikani/commit/6a283447fe1183fbb936f6e69ce74a3726f5381b))

### Feature

* feat: add double check feature. It allows you to set a wrong answer t… (#39)

It is useful when you used a synonym that was not in the word list. ([`ad7dc9b`](https://github.com/ajite/hebikani/commit/ad7dc9bfe645319496fa1df3faceac7283ea8f27))


## v1.5.0 (2022-07-27)

### Feature

* feat: improve reviews queue management (#37)

Reviews are now taken 10 by 10. When completing an item a new item will be added to the queue.

When an item is wrong, the item will go back at the end of the queue after the shuffle.

It avoid the same question to be asked twice in a row. It makes it easier.

Keeping a queue of 10 itwms (max 20 questions or less with radicals), makes it easier to interrupt a session. ([`e127f30`](https://github.com/ajite/hebikani/commit/e127f30883898b1a4f52594592be19434545350f))


## v1.4.5 (2022-07-26)

### Ci

* ci: use browniebroke/python-semantic-release@fix/version-parsing-commit (#35) ([`87ac328`](https://github.com/ajite/hebikani/commit/87ac328dde93f4fd524fb7e0d0e1c33e9dfe843e))

### Fix

* fix(deps): bump sphinx from 5.0.2 to 5.1.0 (#36)

Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 5.0.2 to 5.1.0.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/5.x/CHANGES)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v5.0.2...v5.1.0)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`57cf58b`](https://github.com/ajite/hebikani/commit/57cf58b43a4dda1b7b50650389526f09191e78b9))


## v1.4.4 (2022-07-19)

### Fix

* fix(deps): bump pygobject from 3.42.1 to 3.42.2 (#34)

Bumps [pygobject](https://pygobject.readthedocs.io) from 3.42.1 to 3.42.2.

---
updated-dependencies:
- dependency-name: pygobject
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`2c5d559`](https://github.com/ajite/hebikani/commit/2c5d559c2e5fd984d65b7d5995709b34f34536a6))


## v1.4.3 (2022-07-05)

### Fix

* fix(deps): bump pillow from 9.1.1 to 9.2.0 (#33)

Bumps [pillow](https://github.com/python-pillow/Pillow) from 9.1.1 to 9.2.0.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/9.1.1...9.2.0)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`606eda4`](https://github.com/ajite/hebikani/commit/606eda4e7d11c7da9392364ff20d01c36b74998f))


## v1.4.2 (2022-06-30)

### Fix

* fix(deps): bump requests from 2.28.0 to 2.28.1 (#32)

Bumps [requests](https://github.com/psf/requests) from 2.28.0 to 2.28.1.
- [Release notes](https://github.com/psf/requests/releases)
- [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md)
- [Commits](https://github.com/psf/requests/compare/v2.28.0...v2.28.1)

---
updated-dependencies:
- dependency-name: requests
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`81ef27c`](https://github.com/ajite/hebikani/commit/81ef27cb5309488a12b92cd2e16da47ad969e95b))


## v1.4.1 (2022-06-22)

### Build

* build(deps): bump sphinx from 5.0.1 to 5.0.2 (#30)

Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 5.0.1 to 5.0.2.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/5.x/CHANGES)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v5.0.1...v5.0.2)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`1a804a4`](https://github.com/ajite/hebikani/commit/1a804a41995df06fa29b91c93a810c374307a429))

### Fix

* fix: lesson arrow navigation stopped working (#31)

Using sys.stdin.raw.read(1) was giving the same input for arrow keys.
Switch it back to what it was before but encoded it to utf8 to get ctrl + c ([`d0746e0`](https://github.com/ajite/hebikani/commit/d0746e09daf91265eef15630199988ff60ee0078))


## v1.4.0 (2022-06-17)

### Feature

* feat: prevent sending empty answer and handle ctrl + c in reading (#29)

* feat: prevent sending empty answer and handle ctrl + c

User can&#39;t send empty meaning or reading. A system beep is sent when try to do so.

User can now ctrl + c out of reading questions.

We used the raw.read in linux,osx getch method since windows getch returned binary as well. ([`732b5c2`](https://github.com/ajite/hebikani/commit/732b5c2619da0b6a6942a857158a1875d1f756d8))


## v1.3.3 (2022-06-17)

### Fix

* fix(deps): bump colorama from 0.4.4 to 0.4.5 (#28)

Bumps [colorama](https://github.com/tartley/colorama) from 0.4.4 to 0.4.5.
- [Release notes](https://github.com/tartley/colorama/releases)
- [Changelog](https://github.com/tartley/colorama/blob/master/CHANGELOG.rst)
- [Commits](https://github.com/tartley/colorama/compare/0.4.4...0.4.5)

---
updated-dependencies:
- dependency-name: colorama
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`0836148`](https://github.com/ajite/hebikani/commit/083614899a15cf2ad0a1299502abd7f0db325f76))


## v1.3.2 (2022-06-16)

### Documentation

* docs: fix doc layout for pypi (#25)

Pypi does not like to use raw html tag. ([`485f6ea`](https://github.com/ajite/hebikani/commit/485f6ea177b413fa3abff361e13c53c36bffbe23))

### Fix

* fix: Roll back threading for audio (#26) ([`41e4238`](https://github.com/ajite/hebikani/commit/41e423817b9c8f8df1526b0651b4462ce10f8a44))


## v1.3.1 (2022-06-16)

### Fix

* fix(deps): change to python-romkan-ng (#24) ([`2fbfebb`](https://github.com/ajite/hebikani/commit/2fbfebb249bb39bc0f0039a6ce4620cae8eac60a))


## v1.3.0 (2022-06-16)

### Documentation

* docs: add logo and backstory generated by OpenAI (#22)

use html to center logo in README
change relative URL to https url in order to display images on Pypi ([`6e0bebf`](https://github.com/ajite/hebikani/commit/6e0bebf13944c9938f8feb15e60d283a15508645))

### Feature

* feat: add windows support (#23)

Added mutagen for windows install since playsound has issue playing WaniKani&#39;s mp3
Mutagen removes the mp3 tag and that makes it work on windows.

We are not saving temporary files and delete them manually.
It was making permission error on windows.

Updated documentation to include Windows install.

Updated tests when removing cache (since we are keeping the files and delete them manually)

Removed tests that were checking that windows is not implemented. ([`b9d95ed`](https://github.com/ajite/hebikani/commit/b9d95ed22d16f5b56577f15bdc5f2b56b3f087ad))

### Test

* test: improve test coverage for method that can be tested easily (#21)

We still need to do tests for input_kana and all the while loops. ([`96ee5df`](https://github.com/ajite/hebikani/commit/96ee5dfe1c410ae22f1b6e6fe088f0d313081560))


## v1.2.2 (2022-06-10)

### Build

* build(deps): bump sphinx from 5.0.0 to 5.0.1 (#19)

Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 5.0.0 to 5.0.1.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/5.x/CHANGES)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v5.0.0...v5.0.1)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`a0baeda`](https://github.com/ajite/hebikani/commit/a0baeda73d4977893332a5f9e017dcc200cd5cac))

### Fix

* fix(deps): bump requests from 2.27.1 to 2.28.0 (#20)

Bumps [requests](https://github.com/psf/requests) from 2.27.1 to 2.28.0.
- [Release notes](https://github.com/psf/requests/releases)
- [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md)
- [Commits](https://github.com/psf/requests/compare/v2.27.1...v2.28.0)

---
updated-dependencies:
- dependency-name: requests
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`06ec8e2`](https://github.com/ajite/hebikani/commit/06ec8e2f8fd82e539ea4547d6290d2199972952a))


## v1.2.1 (2022-06-02)

### Build

* build(deps): set coverage as a dev dependency (#18)

* ci: pinned semantic release to v7.28.1

See https://github.com/relekang/python-semantic-release/issues/442 ([`48bf21d`](https://github.com/ajite/hebikani/commit/48bf21d1f016e52370e5553f5649a14741a5bae5))

* build(deps): bump sphinx from 4.5.0 to 5.0.0 (#17)

Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 4.5.0 to 5.0.0.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/5.x/CHANGES)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v4.5.0...v5.0.0)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`4154f58`](https://github.com/ajite/hebikani/commit/4154f58d951e43e1d560261b87e980acbd33218a))

* build(deps): bump coverage from 6.3.2 to 6.4 (#16)

Bumps [coverage](https://github.com/nedbat/coveragepy) from 6.3.2 to 6.4.
- [Release notes](https://github.com/nedbat/coveragepy/releases)
- [Changelog](https://github.com/nedbat/coveragepy/blob/master/CHANGES.rst)
- [Commits](https://github.com/nedbat/coveragepy/compare/6.3.2...6.4)

---
updated-dependencies:
- dependency-name: coverage
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`6332efd`](https://github.com/ajite/hebikani/commit/6332efdc123f03f6b0eb9c371883e9b65cad604a))

### Ci

* ci: depandabot will prefix commit with fix or build (#15)

It will prefix with fix for upgrade on external production library
It will prefix with build for upgrade on external development library ([`cc86846`](https://github.com/ajite/hebikani/commit/cc868461fc6f5cf7b4044920d77ee9f57fe38d8e))

### Documentation

* docs: add chart documentation and fix doc title (#12) ([`9cec866`](https://github.com/ajite/hebikani/commit/9cec866d368f642afa9d177b3e9423c0aab72d73))

### Fix

* fix(deps): Bump pillow from 9.1.0 to 9.1.1 (#14)

Bumps [pillow](https://github.com/python-pillow/Pillow) from 9.1.0 to 9.1.1.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/9.1.0...9.1.1)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`10e6a54`](https://github.com/ajite/hebikani/commit/10e6a549185976321b307d8a1d994d2744d6b88c))

* fix(deps): Bump pillow from 9.1.0 to 9.1.1 (#13)

Bumps [pillow](https://github.com/python-pillow/Pillow) from 9.1.0 to 9.1.1.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/9.1.0...9.1.1)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;

Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`9b48cb9`](https://github.com/ajite/hebikani/commit/9b48cb9a933bab058342938a43c4ca9349775b75))


## v1.2.0 (2022-06-01)

### Feature

* feat: Vertical histogram to display next reviews (#11)

- &#34;summary&#34; displays a vertical histogram of the daily review plan.
- Add test for the histogram and the summary output
- When no next reviews for the day are available display: &#34;No more reviews for today&#34;
- Made a new demo.gif with the new summary output
- Add python freezegun to help testing the histogram (mock date) ([`67fc8a8`](https://github.com/ajite/hebikani/commit/67fc8a846ab34ec478c7937a69d8401720839792))

### Refactor

* refactor: change variable named katana to katakana (#10) ([`3fc723f`](https://github.com/ajite/hebikani/commit/3fc723ffd0ae156c02cc978e884a04b8b13db9ab))


## v1.1.0 (2022-05-31)

### Documentation

* docs: change the doc title name doc to HebiKani (#8) ([`0435831`](https://github.com/ajite/hebikani/commit/0435831d22c721c85669d0539b9d2ac2f8d830b4))

### Feature

* feat: hard mode requires correct kana (#9)

In hard mode when a question has a reading in katakana:
do not accept its hiragana alternative.

E.g: ベッドの下 answer should be ベッドのした and not べっどのした.

In normal mode both  ベッドのした and べっどのした will work. ([`3b0b834`](https://github.com/ajite/hebikani/commit/3b0b8347d8d1ef1d9dd6636b61a295d560b1dae1))


## v1.0.0 (2022-05-30)

### Ci

* ci: use relekang/python-semantic-release action (#5)

The previous action could not upload a release to pypi. ([`951fc4e`](https://github.com/ajite/hebikani/commit/951fc4e0211f3de712471e2a5eabe507d60cafab))

* ci: typo in quality badge branch condition (#3)

It was looking for a branch named master instead of main ([`41798fb`](https://github.com/ajite/hebikani/commit/41798fb8ee356f3a99a5a82b504ef4e3b252dc6d))

* ci: setup semantic-release (#2)

Improve github actions workflows

- do quality check
- then create badge and publish on pypi and github

All the changes on the main branch need to come from PR ([`e3ccb15`](https://github.com/ajite/hebikani/commit/e3ccb1530d4c9915c6766b060664994b21a61930))

### Documentation

* docs: add a cli demo GIF in both doc and readme (#6) ([`888d458`](https://github.com/ajite/hebikani/commit/888d45888dcc8f8ac608c9e06f2fae44a052fe09))

* docs: add the readthedocs badge on README.md ([`623467c`](https://github.com/ajite/hebikani/commit/623467c49a41e363f23c22efe16fd0205caab5ab))

### Fix

* fix: hard mode does not work with inexact answers (#4)

Answers are considered inexact in hard mode when:

1) For a question with 1 acceptable answer:
- Used an unacceptable answer (E.g: onyumi instead of kunyomi)

2) For a question with 2 or more acceptable answer:
- Used the correct number of answers
- One or all of them are unacceptable answers.

* ci: flake8 is taking too long to run

- Ignore .venv and build directory
 - add semantic workflow to check semantic title (will be working for future PR) ([`20df7ca`](https://github.com/ajite/hebikani/commit/20df7caa96d6f1f01f8a49054be51c9d14d51592))

* fix: do not run on debian based system

Add dependencies to run on debian based system.
Add doc to explain dependencies that needs to be added. ([`08cd8da`](https://github.com/ajite/hebikani/commit/08cd8da9cc580a5a9b1cf6fb4776f789bd03103f))

### Refactor

* refactor: renamed project from WaniKani CLI to HebiKani (#7)

You will need to import from hebikani instead of wanikani_cli

BREAKING CHANGE: the library name on PIP is not wanikani-cli anymore. ([`f9a8ebd`](https://github.com/ajite/hebikani/commit/f9a8ebda6c11d772676c1a2edfd711fd83e6ba9d))

### Style

* style: no new line at the end docs/sources/conf.py ([`e451d01`](https://github.com/ajite/hebikani/commit/e451d013a8fdc5d9a9d446c2b706c2642306c854))

### Test

* test: github action fails due to PyGObject

Change the testing OS to macos-latest since it does not requires extra ([`2554fb0`](https://github.com/ajite/hebikani/commit/2554fb06e4d7476f04f955fd278d0e602a24df1d))

### Unknown

* doc: Add readthedocs config file

The doc was not building properly. Add a requirements.txt in doc.
Contains only doc dependency. ([`c935484`](https://github.com/ajite/hebikani/commit/c93548432057fc56735d2057506e3ebc12434ec1))

* fix typo on badge name in README.rst ([`9666796`](https://github.com/ajite/hebikani/commit/96667960cd1f8de21069be5559ee35452a61aee3))

* Add coverage badge through gist and shield.io

Improve github actions to cache poetry install (unless it need new lib) ([`db64777`](https://github.com/ajite/hebikani/commit/db64777cc154843aa8866fb84b2db2493ccb318d))

* Change http_get, post and put to one method

Updated test coverage ([`cf8c6e7`](https://github.com/ajite/hebikani/commit/cf8c6e7ed19c84ac245e3bb81b06e59ef0816682))

* Colorized lessons mnemonics as well ([`b38d04e`](https://github.com/ajite/hebikani/commit/b38d04e5440da5af3743af0688fe0580354b33a1))

* Replaced WaniKani tags by color in mnemonics. ([`b6e6e31`](https://github.com/ajite/hebikani/commit/b6e6e310aa6000ffbcd080ac8548bd230f561c0e))

* Improve lesson layout. Pressing enter goes right.

Improve display layout when doing lessons.
Display number of lesson done and left to do. ([`4e44a23`](https://github.com/ajite/hebikani/commit/4e44a23e3017796d3a23dc2b98cf721e44618445))

* Clear the audio cache when the program ends.

It was working only when the user used ctrl + c ([`bb50ddf`](https://github.com/ajite/hebikani/commit/bb50ddfdcc6893633aa34aadd962801b4f017f1d))

* Update README warning. ([`933d0df`](https://github.com/ajite/hebikani/commit/933d0df2e5741632bb0e6674e1d1c838bb5108ba))

* Cache audio during and play it in a thread.

It is useless to download X times the same audio.
We cache it during our first download.

It will change the alternate method a little bit
since caching keeps the same audio gender.

Audio are download at the begining of a
lessons (with extra character).

Audio are played in a different thread. ([`6c174e9`](https://github.com/ajite/hebikani/commit/6c174e91ba8844a91f7d0e1e3d8b97a53baf49a1))

* Display number of readings in hard mode.

Some kanji have 2 readings while their vocab has only one.
e.g.: 谷. The readings for the kanji are: たに、や.
But the vocabulary only needs one answer: たに.

It feels fairer that way. ([`67bed6c`](https://github.com/ajite/hebikani/commit/67bed6c7340821b03d5b7038964eca30401bea4a))

* Fix forgot to rename _subject_per_ids in test ([`5e89e6f`](https://github.com/ajite/hebikani/commit/5e89e6ff8365a6f3f1452cc6f7f3861a83789683))

* Added lessons

Can navigate through tab to do lessons
Send the lesson results back to API

Added cache when loading subjects in lesson. ([`9ed8316`](https://github.com/ajite/hebikani/commit/9ed83166a4e669f85fcc6b113c8cfcde5e74abd9))

* Fix todo list in README ([`1de68da`](https://github.com/ajite/hebikani/commit/1de68da2f6a6d1436988d5ee4421462ceb198cf9))

* fix readme layout for code display ([`6a472e2`](https://github.com/ajite/hebikani/commit/6a472e28ab99c7bae5bbc108be180dbd6da176ef))

* Improved revewing interface and added mnemonic.

- Added --limit argument to limit the number of reviews in a session.
  The max is 500 and the min is 1.
- Added --mnemonics to diplay question mnemonic when making a mistake
- Catch &#34;ctrl +c&#34; to display an exit message. ([`0c0317e`](https://github.com/ajite/hebikani/commit/0c0317e16c06cd2e256c6b7dfe3b65f14dfa995d))

* Remove alpha notice and change it to experimental release. ([`fae56f1`](https://github.com/ajite/hebikani/commit/fae56f1c0d9ca8bd6ccd045d2e2fea4b71e1bd3c))

* Send reviews back to WaniKani API.

Added a --dry-run for testing purposes.
This mode does not send anything back to the API.

Added a hard mode that will require the user to input
all the prounonciation of a given kanji.
E.g: なに,なん for 何. The order does not matter.

Changed the entire architecture to handle subject.
Removed Kanji, Vocabulary and Radical class.

Create a class to handle Subject update. ([`c85abac`](https://github.com/ajite/hebikani/commit/c85abac1059c2194cf976204f77fbaf0ccff42bc))

* Add a an answer manager object to solve questions

Check for four different types of answers
(Correct, Incorrect, Inexact, A bit off):
- Correct answer (right)
- Incorrect answer (wrong)
- Inexact applies only for reading. When using an non acceptable answer.
  E.g kunyomi instead of onyomi. Inexact methods are calculated through
  python difflib library. We set a constant ratio to 0.8.
- A bit off applies only for meaning. E.g: skillfull instead of skillful

When an answer is inexact we ask the user for the exact meaning.
When an answer is bit off we ask the user to validate his answer.

Moved enums in a file named typing.py ([`7b431f1`](https://github.com/ajite/hebikani/commit/7b431f1863a237078a50108705768b9c832d728a))

* Fix typo in README.rst ([`07ce361`](https://github.com/ajite/hebikani/commit/07ce361501954ce7a3781f5f964df9f2803e57d0))

* Bump version number

We changed the project folder structure. ([`d8fddff`](https://github.com/ajite/hebikani/commit/d8fddff7c7786240833fadf0d335c66e6a8b61e2))

* Use poetry instead of setuptools

- Change package structure
- Add black

Poetry makes it easier to manage dependencies versions and build.
Add specifc lib requirements for Darwin (pyobjc).
Improve README.rst.
Use poetry to generate requirements.txt. ([`fd915d5`](https://github.com/ajite/hebikani/commit/fd915d53143254709e8d70e071f04256d4cee7bb))

* github actions seems to work with setup.py develop ([`c0b615f`](https://github.com/ajite/hebikani/commit/c0b615fcc7b19fffbfa658baf4343a851f46c075))

* Use pip instead of setup.py in Github actions ([`1fcc5ac`](https://github.com/ajite/hebikani/commit/1fcc5acc7bcf0c749c7c1b01b327ebe30b0b1010))

* Add github actions for tests

Runs pytes and flake8 on Python 3.9 ([`928e21c`](https://github.com/ajite/hebikani/commit/928e21c1612db74025c7dcb74ecd4d708be66f40))

* Add .vscode in .gitignore

Added a comment for the Audi class definition ([`038de87`](https://github.com/ajite/hebikani/commit/038de87f86aaed575312fbb1b2d3c8557d952368))

* Merge pull request #1 from RBrearton/main

Small refactoring changes

- Replaced the deprecated OptionParser with the recommended ArgumentParser module.
- Removed COMMANDS, since we can work this out from the Client class.
- Added type hints.
- Added to a few different docstrings, renamed some variables and moved stuff around. ([`d150b16`](https://github.com/ajite/hebikani/commit/d150b16bb6cfb13bfdde3d77f3c45efca73bf764))

* Merge branch &#39;main&#39; into main ([`7bebd74`](https://github.com/ajite/hebikani/commit/7bebd740218b0d1de966f64a06696b4231fb929c))

* Added audio features with playsound.

Created a list of Audio objects when available from the API.
Only play MP3 and ignores OGG.
Changed optparse to argparse (the former being deprecated)
- Added option to autoplay the sound or to be asked.
- Added silent mode
- Can select female, male, alternate or random voice actors ([`25f3a6a`](https://github.com/ajite/hebikani/commit/25f3a6a5cc0ae458d49733b439300630dfa0465b))

* Added type hints, changed some docs ([`254c8aa`](https://github.com/ajite/hebikani/commit/254c8aaf4a690a00d848bb4767ac8e85db1f65cf))

* Minor changes to please pylint ([`9d3a069`](https://github.com/ajite/hebikani/commit/9d3a0698dcfac5530d30087205550a15335c664b))

* CLI can now infer what commands have been implemented ([`b4bd481`](https://github.com/ajite/hebikani/commit/b4bd4812be18e539f85cf4ec1b2b32836b8b519f))

* Removed deprecated OptionParser dependency ([`c6a7b62`](https://github.com/ajite/hebikani/commit/c6a7b62b99311eedae780c095422d1fb10d9b6e8))

* Improve user interface by cleaning the interface.

- Clear the console after each card (ask for user input)
- Display number of reviews left
- Display percentage of correct and wrong answers ([`4f87ebd`](https://github.com/ajite/hebikani/commit/4f87ebda50df69e3369e6a0affcda1c3a9910939))

* Feature display ASCII art for non UTF character.

We download the smallest PNG the API offers (32x32)
then transform it to ASCCI Art thanks to ascii_magic
and pillow. We only do this for radical without
a UTF entry.

Added missing libraries in setup.cfg:

    - romkan
    - ascii_magic
    - pillow ([`677c79c`](https://github.com/ajite/hebikani/commit/677c79cb8d4a605621f2b72e3821183d5a3cf694))

* Add a romaji to kana input method

The user will now have his lower case kana converted to hiragana and
upper case converted to hiragana while answering questions.

Restructured the library and add a console script &#34;wanikani-cli&#34;.
Quick fix to the README to display code-block properly. ([`56e7008`](https://github.com/ajite/hebikani/commit/56e70082c9f0933dbfae0b160c98c9b5fefca937))

* Initial commit.

The client can check your summary.
Start a review session.
Does not send review results to API. ([`083626f`](https://github.com/ajite/hebikani/commit/083626fc584ccf5718f090ff20947b0df3825dbc))
