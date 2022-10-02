SHELL=/bin/bash -e -o pipefail
COMPONENT ?= demo-api
ENVIRONMENT ?= local
IMAGE ?= ${COMPONENT}:${ENVIRONMENT}


COMPOSE_FILE=docker/docker-compose.yaml
DC=docker-compose -p ${COMPONENT} -f ${COMPOSE_FILE}
DOCKERFILE=docker/Dockerfile

.EXPORT_ALL_VARIABLES:

include makefiles/development.mk
include makefiles/test.mk
