# Sure Deployment Cleaner
This CLI tool provides an easily automatable method for cleaning up
past deployments in S3 buckets.
## Installation
You can install the tool in 3 manners which will be discussed below.
### Python Package
Clone this repository and install as you normally would any python module:
```bash
python3 setup.py install
```
or 
```bash
pip3 install .
```

upon succesfull installation you will have access to `depcleaner` in your `$PATH`:

```bash
depcleaner
Usage: depcleaner [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level [INFO|DEBUG|WARN|ERROR]
  --log-destination TEXT
  --log-format [tab|json]
  --help                          Show this message and exit.

Commands:
  deleteafter
  keepx
```

### Docker
A container image has been provided to ease deployment and installation. To use the container image, simply build it like you would any other image:

```bash
docker build . -t depcleaner
```

The image's entrypoint is configued such that so all you have to do is specify options and args as if the tool were locally installed:

```bash
docker run depcleaner
Usage: depcleaner [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level [INFO|DEBUG|WARN|ERROR]
  --log-destination TEXT          [required]
  --log-format [tab|json]
  --help                          Show this message and exit.

Commands:
  deleteafter
  keepx
```

## Usage
The tool currently supports a single command documented below.
### keepx
The `keepx` command allows the user to specify how many of the most recent deployments they wish to keep, while deleting the rest of the deployments.

See the help-text below for information on its usage:

```bash
depcleaner keepx --help
Usage: depcleaner [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level [INFO|DEBUG|WARN|ERROR]
  --log-destination TEXT
  --log-format [tab|json]
  --help                          Show this message and exit.

Commands:
  deleteafter
  keepx
➜  sure git:(main) ✗ depcleaner keepx --help
Usage: depcleaner keepx [OPTIONS]

Options:
  -X, --delete-older-than INTEGER
                                  In this mode the tool will delete all
                                  deployments older than the Xth oldest
                                  deployment  [required]
  -s, --s3-bucket TEXT            S3 bucket containing Sure application
                                  deployments  [required]
  --help                          Show this message and exit.
```
### deleteafter
The `deleteafter` command allows the user to delete any deployments older than X datetime while retaining at least Y deployments. 

```bash
depcleaner deleteafter --help
Usage: depcleaner deleteafter [OPTIONS]

Options:
  -X, --delete-older-than TEXT    In this mode the tool will delete all
                                  deployments older than X timestamp.
                                  [required]
  -Y, --deployments-to-keep INTEGER
                                  Minimum number of deployments to keep
                                  regardless of timestamp.  [required]
  -s, --s3-bucket TEXT            S3 bucket containing Sure application
                                  deployments  [required]
  --help                          Show this message and exit.
  ```
  
  See below for an example of a succesfull `deleteafter` command:

  ```bash
  depcleaner deleteafter  -X "May 1 2025 14:01" -Y 1 -s will-test123
2024-03-18 16:11:17,667 INFO Cleaning up deployments older than May 1 2025 14:01, while keeping minimum of 1
2024-03-18 16:11:18,157 INFO Found 5 deployments in will-test123:
2024-03-18 16:11:18,158 INFO deploy7yueVvKnujzd8q 2024-03-18 19:20:51+00:00
2024-03-18 16:11:18,158 INFO deployrqJIw582V1Baqx 2024-03-18 19:20:54+00:00
2024-03-18 16:11:18,158 INFO deploylVQVUFkoACbACy 2024-03-18 19:20:55+00:00
2024-03-18 16:11:18,158 INFO deploy6dFZ6Jsw8vQtRh 2024-03-18 19:21:00+00:00
2024-03-18 16:11:18,158 INFO deployBbjQzZ1jZlHn1Z 2024-03-18 19:21:03+00:00
2024-03-18 16:11:18,158 INFO The following 4 deployments will be deleted:
2024-03-18 16:11:18,159 INFO deploy7yueVvKnujzd8q 2024-03-18 19:20:51+00:00
2024-03-18 16:11:18,159 INFO deployrqJIw582V1Baqx 2024-03-18 19:20:54+00:00
2024-03-18 16:11:18,159 INFO deploylVQVUFkoACbACy 2024-03-18 19:20:55+00:00
2024-03-18 16:11:18,159 INFO deploy6dFZ6Jsw8vQtRh 2024-03-18 19:21:00+00:00
2024-03-18 16:11:18,419 INFO Succesfull deleted deploy7yueVvKnujzd8q/index.html
2024-03-18 16:11:18,473 INFO Succesfull deleted deploy7yueVvKnujzd8q/index.js
2024-03-18 16:11:18,528 INFO Succesfull deleted deploy7yueVvKnujzd8q/style.css
2024-03-18 16:11:18,609 INFO Succesfull deleted deployrqJIw582V1Baqx/index.html
2024-03-18 16:11:18,669 INFO Succesfull deleted deployrqJIw582V1Baqx/index.js
2024-03-18 16:11:18,729 INFO Succesfull deleted deployrqJIw582V1Baqx/style.css
2024-03-18 16:11:18,786 INFO Succesfull deleted deploylVQVUFkoACbACy/index.html
2024-03-18 16:11:18,844 INFO Succesfull deleted deploylVQVUFkoACbACy/index.js
2024-03-18 16:11:18,912 INFO Succesfull deleted deploylVQVUFkoACbACy/style.css
2024-03-18 16:11:18,966 INFO Succesfull deleted deploy6dFZ6Jsw8vQtRh/index.html
2024-03-18 16:11:19,026 INFO Succesfull deleted deploy6dFZ6Jsw8vQtRh/index.js
2024-03-18 16:11:19,088 INFO Succesfull deleted deploy6dFZ6Jsw8vQtRh/style.css
```


## Testing
Given the sensitive nature of the operation being performed by this tool, it is imperative we are able to test that its behavior conforms to our expectations and requirements. 

To this end, a test suite has been integrated that utilizes `localstack` to simulate S3, and deploys mock deployments on which to test the tool against. 

Testing locally during development is a good practice, but it is critical for CI/CD. In order to integrate in a CI/CD pipeline we need a way to easily setup our test environment, create a bucket, and run the tests.

A `docker-compose.yaml` file has been included that accomplishes all of these goals. 

To run the tests automatically first build the stack:

```bash
docker-compose build
```
once the images have finished building, you are ready to run the tests.

```bash
docker-compose run depcleaner-test-runner
```
if tests are succesfull you should see an output similar to:

```bash
 docker-compose run depcleaner-test-runner
[+] Creating 2/0
 ✔ Container sure-localstack-1       Running                                                                                                    0.0s 
 ✔ Container sure-setup-assistant-1  Created                                                                                                    0.0s 
[+] Running 1/0
 ✔ Container sure-setup-assistant-1  Started                                                                                                    0.1s 
Setting up test environment with 12 mock deployments...
Populating mock deployment:deploybLNv9S7RxXiIYb
Populating mock deployment:deployGyfvdwlEM7MrgE
Populating mock deployment:deploycY3EMT8MRS2U30
Populating mock deployment:deployZStx5gC6fjRFKD
Populating mock deployment:deployxt55tgEwvJuidh
Populating mock deployment:deployuBBFFrbT5PRpoz
Populating mock deployment:deployG8MQySfPngpzFT
Populating mock deployment:deployHc5V2TzWBB5TCQ
Populating mock deployment:deployoGnhA7LDuc9IXU
Populating mock deployment:deploy7BdNFMOLwwDexV
Populating mock deployment:deployEnFkchfrT3wQ0W
Populating mock deployment:deployFV5pWJOozk6YN5
..
----------------------------------------------------------------------
Ran 2 tests in 39.648s

OK
```
## Questions/Assumptions
### Questions
1. Where should we run this script? 
  - This script should be deployed as a Lambda function with scheduled execution (either containerized or naive Python) or run as a reoccuring job on a production Kubernetes cluster.  Either of these mechanisms will be more robust than leveraging cron on a single Linux machine. 

  In the case of deploying on AWS, Terraform, Cloudformation, or similar level of abstraction deployment tool should be utilized. 

  For Kubernetes simply K8s yaml should suffice given the simplicity of the tool. 

2. How should we test the script before running it production?
 - See ##Testing
3. If we want to add an additional requirement of deleting deploys older than X days but we must maintain at least Y number of deploys. What additional changes would you need to make in the script?
 - See line 99 of src/backend/deploy_cleaner.py
 - If we wanted to change the requirements to include this I would add additional tests for this scenario
### Assumptions
1. All files in deployment were deployed at roughly the same time (i.e. files within a deployment were not modified at a later date). This is important as S3 only stores modified time.
2. Deployment names are unique. No top level S3 prefix contains more than 1 deployment
3. The sub-directory structure is not important to this script.  File names may change over time, etc..
4. The cardinality of the S3 bucket is unknown and could be large
5. We assume the bucket exists and do not check for existance prior to searching for deployments
6. The operator will run the this utility on a machine that has an IAM role with correct permissions, or will have access to AWS credentials as environment variables
7. All timestamps entered are UTC