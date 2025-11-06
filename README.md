Here’s the same doc with a simple matrix table added (you can paste/adjust repo names as needed):

```wiki
= FOSSA Testing Matrix =

== Overview ==
This page documents the sample applications used to validate FOSSA across our supported languages and package managers.  
Each language has its own repository containing a minimal "hello world" style project plus dependencies for FOSSA scanning.

== Covered Languages ==

* Go
* Python
** Pip, Pipenv, Poetry, Conda
** Django, FastAPI, Flask samples (within Python repo)
* PHP
* Java (Maven, Gradle)
* Node.js (npm, Yarn)
* C# (NuGet)

== Repository Layout ==

Each language lives in a dedicated repo, for example:

* <code>fossa-go-hello</code>
* <code>fossa-python-hello</code>
* <code>fossa-php-hello</code>
* <code>fossa-java-maven-hello</code>
* <code>fossa-java-gradle-hello</code>
* <code>fossa-node-npm-hello</code>
* <code>fossa-node-yarn-hello</code>
* <code>fossa-csharp-hello</code>

== Matrix (High-Level) ==

{| class="wikitable"
! Language !! Repository !! Sample Contents !! FOSSA Status
|-
| Go || fossa-go-hello || go_hello || Pass
|-
| Python || fossa-python-hello || python_hello, django_hello, fastapi_hello, flask_hello, python_pipenv_hello, python_conda_hello || Pass
|-
| PHP || fossa-php-hello || php_composer_hello || Pass
|-
| Java (Maven) || fossa-java-maven-hello || java_maven_hello || Pass
|-
| Java (Gradle) || fossa-java-gradle-hello || java_gradle_hello || Pass
|-
| Node.js (npm) || fossa-node-npm-hello || nodejs_npm_hello || Pass
|-
| Node.js (Yarn) || fossa-node-yarn-hello || nodejs_yarn_hello || Pass
|-
| C# || fossa-csharp-hello || csharp_nuget_hello || Pass
|}

== How FOSSA Is Used ==

In each repo:
<pre>
fossa analyze
fossa test
</pre>

GitLab CI example:
<pre>
fossa_scan:
  stage: scan
  script:
    - fossa analyze
    - fossa test
  only:
    - main
    - merge_requests
</pre>

== Maintenance ==
Updates to samples or policies should be reflected here and in each repo’s README.
```

If any repo names differ internally, just update the second column of the table.
