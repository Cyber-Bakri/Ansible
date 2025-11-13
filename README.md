===== FOSSA testing matrix =====

== Overview ==

This repository contains a comprehensive testing matrix for FOSSA (Free and Open Source Software Analysis) across multiple programming languages and their respective package managers. The purpose is to validate FOSSA's ability to detect, scan, and analyze dependencies across different technology stacks.

== Table of Contents ==

# [[#Covered Languages and Package Managers|Covered Languages and Package Managers]]
# [[#Project Structure|Project Structure]]
# [[#Sample Repositories|Sample Repositories]]
# [[#Prerequisites|Prerequisites]]
# [[#Setup Instructions|Setup Instructions]]
# [[#Running Tests|Running Tests]]
# [[#FOSSA Integration|FOSSA Integration]]
# [[#Test Results|Test Results]]
# [[#Troubleshooting|Troubleshooting]]

----

== Covered Languages and Package Managers ==

{| class="wikitable"
! Language !! Package Managers !! Status
|-
| '''Go''' || Go Modules || ✅ Covered
|-
| '''Python''' || Pip, Pipenv, Poetry, Conda || ✅ Covered
|-
| '''PHP''' || Composer || ✅ Covered
|-
| '''Java''' || Maven, Gradle || ✅ Covered
|-
| '''Node.js''' || NPM, Yarn || ✅ Covered
|-
| '''C#''' || NuGet || ✅ Covered
|}

----

== Project Structure ==

<pre>
SO/
├── go_hello/                    # Go with Go Modules
├── python_hello/                # Python with Pip
├── python_pipenv_hello/         # Python with Pipenv
├── python_poetry_hello/         # Python with Poetry
├── python_conda_hello/          # Python with Conda
├── php_composer_hello/          # PHP with Composer
├── java_maven_hello/            # Java with Maven
├── java_gradle_hello/           # Java with Gradle
├── nodejs_npm_hello/            # Node.js with NPM
├── nodejs_yarn_hello/           # Node.js with Yarn
├── csharp_nuget_hello/          # C# with NuGet
├── django_hello/                # Django framework (Python)
├── fastapi_hello/               # FastAPI framework (Python)
├── flask_hello/                 # Flask framework (Python)
├── .gitlab-ci.yml               # CI/CD pipeline configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # Repository overview
</pre>

----

== Sample Repositories ==

Each language has a dedicated repository for FOSSA testing:

{| class="wikitable"
! Language !! Repository !! Sample Contents !! FOSSA Status
|-
| Go || [https://gitlab.us.bank-dns.com/OSPO/fossa-go-hello fossa-go-hello] || go_hello || Pass
|-
| Python || [https://gitlab.us.bank-dns.com/OSPO/python-test-apps python-test-apps] || python_hello, django_hello, fastapi_hello, flask_hello, python_pipenv_hello, python_conda_hello || Pass
|-
| PHP || [https://gitlab.us.bank-dns.com/OSPO/php-fossa-demo php-fossa-demo] || php-fossa-demo || Pass
|-
| Java (Maven) || [https://gitlab.us.bank-dns.com/OSPO/fossa-maven-demo fossa-maven-demo] || java_maven_hello || Pass
|-
| Java (Gradle) || [https://gitlab.us.bank-dns.com/OSPO/fossa-gradle-demo fossa-gradle-demo] || java_gradle_hello || Pass
|-
| Node.js (npm) || [https://gitlab.us.bank-dns.com/OSPO/fossa-javascript-demo fossa-javascript-demo] || nodejs_npm_hello || Pass
|-
| Node.js (Yarn) || fossa-node-yarn-hello || nodejs_yarn_hello || Pass
|-
| C# || [https://gitlab.us.bank-dns.com/OSPO/fossa-dotnet-demo fossa-dotnet-demo] || csharp_nuget_hello || Pass
|}

----

== Prerequisites ==

=== General Requirements ===

* FOSSA CLI installed ([https://github.com/fossas/fossa-cli Installation Guide])
* Git
* Access to FOSSA dashboard/account
* Access to GitLab OSPO organization
* Access to Shield Console and Pipeline Templates

=== Language-Specific Requirements ===

==== Go ====

* Go 1.18+ installed
* <code>go mod</code> support enabled

==== Python ====

* Python 3.8+ installed
* pip (bundled with Python)
* Pipenv: <code>pip install pipenv</code>
* Poetry: <code>pip install poetry</code>
* Conda/Miniconda: [https://docs.conda.io/en/latest/miniconda.html Download]

==== PHP ====

* PHP 7.4+ or 8.x
* Composer: [https://getcomposer.org/download/ Download]

==== Java ====

* JDK 11+ installed
* Maven 3.6+: [https://maven.apache.org/download.cgi Download]
* Gradle 7.0+: [https://gradle.org/install/ Download]

==== Node.js ====

* Node.js 14+ and npm (bundled)
* Yarn: <code>npm install -g yarn</code>

==== C# ====

* .NET SDK 6.0+: [https://dotnet.microsoft.com/download Download]
* NuGet CLI (optional)

----

== Setup Instructions ==

=== Clone the Repository ===

Choose the appropriate repository based on the language you're testing:

<syntaxhighlight lang="bash">
# Example: Clone the Python test apps repository
git clone https://gitlab.us.bank-dns.com/OSPO/python-test-apps.git
cd python-test-apps

# Example: Clone the Go hello repository
git clone https://gitlab.us.bank-dns.com/OSPO/fossa-go-hello.git
cd fossa-go-hello
</syntaxhighlight>

=== Go Project Setup ===

<syntaxhighlight lang="bash">
cd go_hello
go mod download
go build
</syntaxhighlight>

=== Python Projects Setup ===

==== Pip (Standard Python) ====

<syntaxhighlight lang="bash">
cd python_hello
pip install -r requirements.txt
</syntaxhighlight>

==== Pipenv ====

<syntaxhighlight lang="bash">
cd python_pipenv_hello
pipenv install
pipenv shell
</syntaxhighlight>

==== Poetry ====

<syntaxhighlight lang="bash">
cd python_poetry_hello
poetry install
poetry shell
</syntaxhighlight>

==== Conda ====

<syntaxhighlight lang="bash">
cd python_conda_hello
conda env create -f environment.yml
conda activate python-conda-hello
</syntaxhighlight>

=== PHP Project Setup ===

<syntaxhighlight lang="bash">
cd php_composer_hello
composer install
</syntaxhighlight>

=== Java Projects Setup ===

==== Maven ====

<syntaxhighlight lang="bash">
cd java_maven_hello
mvn clean install
</syntaxhighlight>

==== Gradle ====

<syntaxhighlight lang="bash">
cd java_gradle_hello
gradle build
</syntaxhighlight>

=== Node.js Projects Setup ===

==== NPM ====

<syntaxhighlight lang="bash">
cd nodejs_npm_hello
npm install
</syntaxhighlight>

==== Yarn ====

<syntaxhighlight lang="bash">
cd nodejs_yarn_hello
yarn install
</syntaxhighlight>

=== C# Project Setup ===

<syntaxhighlight lang="bash">
cd csharp_nuget_hello
dotnet restore
dotnet build
</syntaxhighlight>

----

== Running Tests ==

=== Running Application Tests ===

Each project includes unit tests to verify functionality:

==== Go ====

<syntaxhighlight lang="bash">
cd go_hello
go test ./...
</syntaxhighlight>

==== Python (general) ====

<syntaxhighlight lang="bash">
# Using pytest
pytest

# Using unittest
python -m unittest discover
</syntaxhighlight>

==== PHP ====

<syntaxhighlight lang="bash">
cd php_composer_hello
./vendor/bin/phpunit
</syntaxhighlight>

==== Java (Maven) ====

<syntaxhighlight lang="bash">
cd java_maven_hello
mvn test
</syntaxhighlight>

==== Java (Gradle) ====

<syntaxhighlight lang="bash">
cd java_gradle_hello
gradle test
</syntaxhighlight>

==== Node.js ====

<syntaxhighlight lang="bash">
# NPM
npm test

# Yarn
yarn test
</syntaxhighlight>

==== C# ====

<syntaxhighlight lang="bash">
dotnet test
</syntaxhighlight>

----

== FOSSA Integration ==

=== Local FOSSA CLI Usage ===

For local testing and manual analysis, you can use FOSSA CLI commands:

<syntaxhighlight lang="bash">
# Initialize FOSSA in a project
fossa init

# Run FOSSA analysis
fossa analyze

# Run FOSSA test (check for license compliance)
fossa test
</syntaxhighlight>

{{Note|When using the CI/CD pipeline, '''do not''' manually run <code>fossa analyze</code>. The Shield Pipeline templates handle FOSSA scanning automatically.}}

----

=== CI/CD Integration with Shield Pipeline Templates ===

==== Overview ====

All FOSSA test repositories use the '''Shield Pipeline''' templates from the <code>engineering/pipelinecli</code> project. These shared templates provide standardized CI/CD workflows that include:

* Automated dependency installation
* Unit testing
* '''FOSSA dependency scanning''' (when enabled)
* Security scanning with Twistlock, Blackduck, and Fortify
* Integration with SHIELD platform tools

{{Note|'''Critical:''' Do NOT manually call <code>fossa analyze</code> in your pipeline scripts. The Shield Pipeline plugins automatically handle FOSSA scanning when <code>RUN_FOSSA_ANALYSIS: "true"</code> is set in your job configuration.}}

==== How It Works ====

# '''Include the Template''': Your <code>.gitlab-ci.yml</code> references shared templates from <code>engineering/pipelinecli</code>
# '''Extend a Template Job''': Your job extends a language-specific template (e.g., <code>.python-build-and-analyze-template</code>)
# '''Set Required Variables''': Configure METTA, SHIELD, CARID, LOB, and enable FOSSA analysis
# '''Define Your Stages''': Specify pipeline stages like <code>test-and-scan</code> or <code>install & scan</code>
# '''Let Templates Handle the Rest''': The template automatically installs dependencies, runs tests, and performs FOSSA scanning

==== Quick Start ====

To add FOSSA scanning to your project:

# Include the Shield Pipeline template in your <code>.gitlab-ci.yml</code>
# Set <code>RUN_FOSSA_ANALYSIS: "true"</code> in your job variables
# Extend the appropriate template for your language/framework
# Push your changes and let the pipeline run

==== Resources ====

{| class="wikitable"
! Resource !! Description !! Link
|-
| '''Shield Pipeline Documentation''' || Complete guide on using pipeline templates || [https://shield-console.us.bank-dns.com/docs/default/component/plat-shieldplatform-shielddocs/extern/pipelinecli/ Shield Pipeline Docs]
|-
| '''Pipeline Templates Repository''' || Browse available templates and plugins || [https://gitlab.us.bank-dns.com/engineering/pipelinecli/-/tree/latest/templates/plugins?ref_type=heads PipelineCLI Templates]
|-
| '''Plugin Shared Options''' || Available template jobs and configuration options || [https://shield-console.us.bank-dns.com/docs/default/component/plat-shieldplatform-shielddocs/extern/pipelinecli/ Plugin Documentation]
|-
| '''OSPO Sample Repositories''' || Working examples for each language || [https://gitlab.us.bank-dns.com/OSPO OSPO Organization]
|}

==== Available Template Jobs by Language ====

{| class="wikitable"
! Language/Framework !! Template Job to Extend !! Pipeline Stage
|-
| Node.js (npm) || <code>.nodejs-20-install-scan-template</code> || <code>install & scan</code>
|-
| Python (all managers) || <code>.python-build-and-analyze-template</code> || <code>test-and-scan</code>
|-
| Java (Maven) || <code>.maven-build-and-analyze-template</code> || <code>build-and-scan</code>
|-
| Java (Gradle) || <code>.gradle-build-and-analyze-template</code> || <code>build-and-scan</code>
|-
| PHP (Composer) || <code>.php-build-and-analyze-template</code> || <code>build-and-scan</code>
|-
| C# (NuGet) || <code>.dotnet-build-and-analyze-template</code> || <code>build-and-scan</code>
|-
| Go (Modules) || <code>.go-build-and-analyze-template</code> || <code>build-and-scan</code>
|}

==== Example Pipeline Structure ====

A typical FOSSA-enabled pipeline follows this structure:

<syntaxhighlight lang="yaml">
# 1. Include the shared template
include:
  - project: 'engineering/pipelinecli'
    file: '/templates/plugins/plugin-steps.yml'
    ref: latest

# 2. Define global variables
variables:
  METTA_APPLICATION: "your-app-name"
  SHIELD_TEAM: "your-team-name"
  CARID: 9895
  LOB: "OSPO"

# 3. Define stages
stages:
  - test-and-scan

# 4. Create job that extends template
your-job-name:
  extends: .python-build-and-analyze-template
  stage: test-and-scan
  variables:
    RUN_FOSSA_ANALYSIS: "true"  # This enables FOSSA scanning!
    WORK_DIR: your_project_dir
</syntaxhighlight>

For complete configuration examples, see the [https://gitlab.us.bank-dns.com/OSPO OSPO sample repositories].

==== Key Configuration Variables ====

When enabling FOSSA analysis, you'll need to set these variables:

'''Required Global Variables:'''
* <code>METTA_APPLICATION</code> - Your application name in Metta
* <code>METTA_COMPONENT</code> - Component identifier
* <code>SHIELD_TEAM</code> - Your SHIELD team name
* <code>CARID</code> - Your application's CAR ID
* <code>LOB</code> - Line of Business
* <code>FOSSA_API_KEY</code> - Set as protected CI/CD variable

'''Required Job Variables:'''
* <code>RUN_FOSSA_ANALYSIS: "true"</code> - Enables FOSSA scanning in the pipeline

'''Optional Python-Specific Variables:'''
* <code>WORK_DIR</code> - Subdirectory containing your Python project
* <code>PYTHON_VIRTUALENV</code> - Virtual environment name
* <code>PYTHON_BUILD_PACKAGE</code> - Whether to build a package
* <code>PYTHON_BUILD_FRAMEWORK</code> - Build tool (setupy, build, poetry, etc.)

For a complete list of variables, consult the [https://shield-console.us.bank-dns.com/docs/default/component/plat-shieldplatform-shielddocs/extern/pipelinecli/ Shield Pipeline Documentation].

=== Detected Dependency Files by Language ===

FOSSA automatically detects and analyzes the following dependency manifest files:

{| class="wikitable"
! Language !! Dependency File(s) !! FOSSA Detection
|-
| Go || <code>go.mod</code>, <code>go.sum</code> || ✅ Automatic
|-
| Python (Pip) || <code>requirements.txt</code>, <code>setup.py</code> || ✅ Automatic
|-
| Python (Pipenv) || <code>Pipfile</code>, <code>Pipfile.lock</code> || ✅ Automatic
|-
| Python (Poetry) || <code>pyproject.toml</code>, <code>poetry.lock</code> || ✅ Automatic
|-
| Python (Conda) || <code>environment.yml</code> || ✅ Automatic
|-
| PHP || <code>composer.json</code>, <code>composer.lock</code> || ✅ Automatic
|-
| Java (Maven) || <code>pom.xml</code> || ✅ Automatic
|-
| Java (Gradle) || <code>build.gradle</code>, <code>settings.gradle</code> || ✅ Automatic
|-
| Node.js (NPM) || <code>package.json</code>, <code>package-lock.json</code> || ✅ Automatic
|-
| Node.js (Yarn) || <code>package.json</code>, <code>yarn.lock</code> || ✅ Automatic
|-
| C# || <code>*.csproj</code>, <code>packages.config</code> || ✅ Automatic
|}

----

== Test Results ==

=== Test Coverage Matrix ===

{| class="wikitable"
! Project !! Build Status !! Test Status !! FOSSA Scan !! Dependencies Detected
|-
| go_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| python_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| python_pipenv_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| python_poetry_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| python_conda_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| php_composer_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| java_maven_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| java_gradle_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| nodejs_npm_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| nodejs_yarn_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| csharp_nuget_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| django_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| fastapi_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|-
| flask_hello || ✅ Pass || ✅ Pass || ✅ Pass || Yes
|}

=== Key Findings ===

# '''Dependency Detection''': FOSSA successfully detected dependencies across all package managers
# '''License Compliance''': All projects passed license compliance checks
# '''Vulnerability Scanning''': Security vulnerabilities were identified and documented
# '''Performance''': Average scan time ranged from 30 seconds (Go) to 3 minutes (Java Gradle)

----

== Troubleshooting ==

=== Common Issues ===

==== FOSSA CLI Not Found ====

<syntaxhighlight lang="bash">
# Install FOSSA CLI
curl -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/fossas/fossa-cli/master/install-latest.sh | bash
</syntaxhighlight>

==== Authentication Issues ====

<syntaxhighlight lang="bash">
# Set FOSSA API key
export FOSSA_API_KEY=your-api-key-here
</syntaxhighlight>

==== FOSSA Scan Failing in CI/CD ====

If your FOSSA scan is failing in the pipeline:

# '''Verify RUN_FOSSA_ANALYSIS is set''': Ensure <code>RUN_FOSSA_ANALYSIS: "true"</code> is in your job variables
# '''Check template reference''': Confirm you're including the correct template from <code>engineering/pipelinecli</code>
# '''Verify API key''': Confirm <code>FOSSA_API_KEY</code> is set in CI/CD variables (Settings → CI/CD → Variables)
# '''Check template extension''': Make sure you're extending the right template for your language
# '''Review Shield Pipeline docs''': Consult [https://shield-console.us.bank-dns.com/docs/default/component/plat-shieldplatform-shielddocs/extern/pipelinecli/ Shield Pipeline Documentation]

==== Template Not Found Error ====

If you get an error about template not found:

# Verify your include block references <code>engineering/pipelinecli</code>
# Check that you're using <code>ref: latest</code> or a valid branch/tag
# Ensure you have access to the pipelinecli repository

==== Go Module Issues ====

<syntaxhighlight lang="bash">
# Clear module cache
go clean -modcache
go mod download
</syntaxhighlight>

==== Python Virtual Environment Issues ====

<syntaxhighlight lang="bash">
# Pipenv
pipenv --rm
pipenv install

# Poetry
poetry env remove python
poetry install

# Conda
conda env remove -n python-conda-hello
conda env create -f environment.yml
</syntaxhighlight>

==== Node.js Lock File Conflicts ====

<syntaxhighlight lang="bash">
# NPM
rm package-lock.json node_modules -rf
npm install

# Yarn
rm yarn.lock node_modules -rf
yarn install
</syntaxhighlight>

==== Java Build Failures ====

<syntaxhighlight lang="bash">
# Maven - clean and rebuild
mvn clean install -U

# Gradle - clean and rebuild
gradle clean build --refresh-dependencies
</syntaxhighlight>

==== C# Restore Issues ====

<syntaxhighlight lang="bash">
# Clear NuGet cache
dotnet nuget locals all --clear
dotnet restore --force
</syntaxhighlight>

=== Language-Specific Notes ===

==== Python ====

* Ensure virtual environments are activated before running tests
* Some packages may require system-level dependencies (e.g., <code>psycopg2</code> needs PostgreSQL dev libraries)
* Set <code>WORK_DIR</code> variable to point to your specific Python project directory

==== Java ====

* Gradle builds may take longer on first run due to dependency downloads
* Ensure <code>JAVA_HOME</code> is set correctly

==== Node.js ====

* Use <code>nvm</code> (Node Version Manager) to manage multiple Node.js versions
* Some packages may require native build tools
* Ensure <code>node_modules/</code> is included in artifacts if needed by downstream jobs

==== C# ====

* Ensure .NET SDK version matches project requirements
* Some packages may require Windows-specific dependencies

----

== Contributing ==

To add a new language or package manager to the testing matrix:

# Create a new directory: <code><language>_<package_manager>_hello/</code>
# Add a simple "Hello World" application
# Include at least 2-3 dependencies
# Add unit tests
# Create a <code>.gitlab-ci.yml</code> that:
#* Includes the <code>engineering/pipelinecli</code> template
#* Extends the appropriate language template
#* Sets <code>RUN_FOSSA_ANALYSIS: "true"</code>
# Create a README.md specific to that project
# Update this wiki page
# Test FOSSA scanning in your pipeline
# Submit a merge request to the appropriate OSPO repository

Refer to existing [https://gitlab.us.bank-dns.com/OSPO OSPO repositories] for configuration examples.

----

== References ==

* [https://shield-console.us.bank-dns.com/docs/default/component/plat-shieldplatform-shielddocs/extern/pipelinecli/ Shield Pipeline Documentation] - '''Primary resource for CI/CD setup'''
* [https://gitlab.us.bank-dns.com/engineering/pipelinecli/-/tree/latest/templates/plugins?ref_type=heads Pipeline Templates Repository]
* [https://docs.fossa.com/ FOSSA Documentation]
* [https://github.com/fossas/fossa-cli FOSSA CLI GitHub]
* [https://fossa.com/learn License Compliance Best Practices]
* [https://gitlab.us.bank-dns.com/OSPO OSPO GitLab Organization]

----

== License ==

This testing matrix repository is for internal testing purposes. Individual projects may have different licenses - refer to each project's LICENSE file.

----

'''Last Updated''': November 13, 2025<br>
'''Maintained By''': Development Team<br>
'''FOSSA Version''': 3.x
