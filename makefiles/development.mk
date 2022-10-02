.PHONY: attach
attach: ## Attach to running server for debugging. Ctrl+D to detach.
attach: instance  ?= 1
attach:
	docker attach --detach-keys="ctrl-d" ${COMPONENT}_development_${instance}

.PHONY: build
build: ## Build containers
build: prod_image?= ${COMPONENT}:${ENVIRONMENT}
build: dev_image?= ${COMPONENT}_development:${ENVIRONMENT}
build: args?= -f docker/Dockerfile
build:
	docker pull python:3.9-slim
	DOCKER_BUILDKIT=1 docker build --progress=plain --target production -t ${prod_image} --build-arg BUILDKIT_INLINE_CACHE=1 ${args} ..
	DOCKER_BUILDKIT=1 docker build --progress=plain --target development -t ${dev_image} --build-arg BUILDKIT_INLINE_CACHE=1 --cache-from ${prod_image} ${args} ..

.PHONY: clean
clean: ## Stop and remove containers created by up command.
	${DC} down --remove-orphans


.PHONY: logs
logs: ## Show logs for the current project.
	${DC} logs -f

.PHONY: reformat
reformat: files ?= .
reformat: ## Fix lint/format
	${DC} run -v $(PWD):/srv/app --rm --no-deps black --line-length 120 ${files}
	${DC} run -v $(PWD):/srv/app --rm --no-deps isort --line-length 120 ${files}

.PHONY: develop
develop: ## Start a docker instance with docker-compose.
	touch ./docker/local.env
	${DC} up -d development

.PHONY: deploy
deploy: ## Start a docker instance with docker-compose.
	touch ./docker/local.env
	${DC} up -d server

.PHONY: retry
retry: ## Full restart
	build develop attach ## Full restart
