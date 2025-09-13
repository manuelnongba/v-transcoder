REGISTRY = manuelnongba

build-auth:
	docker build -t $(REGISTRY)/auth:latest auth/

build-gateway:
	docker build -t $(REGISTRY)/gateway:latest gateway/

build-converter:
	docker build -t $(REGISTRY)/converter:latest converter/

build-notification:
	docker build -t $(REGISTRY)/notification:latest notification/

build-transcriber:
	docker build -t $(REGISTRY)/transcriber:latest transcriber/

build-translator:
	docker build -t $(REGISTRY)/translator:latest translator/

build-all: build-auth build-gateway build-converter build-notification build-transcriber build-translator

push-auth:
	docker push $(REGISTRY)/auth:latest

push-gateway:
	docker push $(REGISTRY)/gateway:latest

push-converter:
	docker push $(REGISTRY)/converter:latest

push-notification:
	docker push $(REGISTRY)/notification:latest

push-transcriber:
	docker push $(REGISTRY)/transcriber:latest

push-translator:
	docker push $(REGISTRY)/translator:latest

push-all: push-auth push-gateway push-converter push-notification push-transcriber push-translator

deploy-rabbit:
	kubectl apply -f rabbit/manifest/

deploy-auth:
	kubectl apply -f auth/manifest/

deploy-converter:
	kubectl apply -f converter/manifest/

deploy-notification:
	kubectl apply -f notification/manifest/

deploy-gateway:
	kubectl apply -f gateway/manifest/

deploy-transcriber:
	kubectl apply -f transcriber/manifest/

deploy-translator:
	kubectl apply -f translator/manifest/

deploy-all: deploy-rabbit deploy-auth deploy-converter deploy-notification deploy-gateway deploy-transcriber deploy-translator

start:
	minikube start

stop:
	minikube stop

tunnel:
	minikube tunnel

status:
	kubectl get pods
	kubectl get services

pods-auth:
	kubectl get pods -l app=auth

pods-gateway:
	kubectl get pods -l app=gateway

pods-converter:
	kubectl get pods -l app=converter

pods-notification:
	kubectl get pods -l app=notification

pods-transcriber:
	kubectl get pods -l app=transcriber

pods-translator:
	kubectl get pods -l app=translator

list-queues:
	kubectl exec rabbitmq-0 -- rabbitmqctl list_queues

remove:
	kubectl delete -f gateway/manifest/
	kubectl delete -f notification/manifest/
	kubectl delete -f converter/manifest/
	kubectl delete -f auth/manifest/
	kubectl delete -f transcriber/manifest/
	kubectl delete -f translator/manifest/
	kubectl delete -f rabbit/manifest/

clean:
	kubectl delete all --all
	docker rmi $(REGISTRY)/auth:latest $(REGISTRY)/gateway:latest $(REGISTRY)/converter:latest $(REGISTRY)/notification:latest $(REGISTRY)/transcriber:latest $(REGISTRY)/translator:latest 2>/dev/null || true
