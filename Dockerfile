FROM andyceo/pylibs
COPY ["config-sample.ini", "node-info-monitor.py", "/app/"]
ENTRYPOINT ["/app/node-info-monitor.py"]
CMD ["sync-daemon"]
