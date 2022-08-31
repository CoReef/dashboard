build:
	docker build -t dashboard_image .
run:
	docker run -d --restart=unless-stopped -p 4343:4343 -v v_coreef:/coreef --name dashboard_coreef dashboard_image
clean:
	find . -name '__pycache__' | xargs rm -rf;
