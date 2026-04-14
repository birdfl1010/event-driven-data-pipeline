IMAGE_NAME=artifactory.bird.com:8443/internalsystems/middleware/api/vendor_rewards_processor
IMAGE_TAG=latest
IMAGESTREAM_NAME=vendor_rewards_processor

.PHONY: build
build:
	@echo Recording version information thru app.version
	git rev-parse --abbrev-ref HEAD > app.version
	git log -n 1 >> app.version
	@echo building container
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

deploy:
	@echo Deploying container
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	@echo Accessing openshift to import the image
	oc import-image $(IMAGESTREAM_NAME):$(IMAGE_TAG)