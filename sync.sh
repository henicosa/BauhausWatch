#!/bin/bash
rsync -avz --info=progress2 -e "ssh -F /home/llorenz/.ssh/config" "." strato:/root/docker-sources/BauhausWatch
rsync -avz --info=progress2 -e "ssh -F /home/llorenz/.ssh/config" "." m18:/home/ludwig/docker-sources/BauhausWatch