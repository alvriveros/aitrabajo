FROM scratch
COPY r/ /
ENV PIP_CERT=/ca/ca-bundle.crt PATH=/usr/local/bin:/usr/bin:/bin LD_LIBRARY_PATH=/usr/local/lib:/lib/x86_64-linux-gnu PIP_BREAK_SYSTEM_PACKAGES=1 HOME=/root
