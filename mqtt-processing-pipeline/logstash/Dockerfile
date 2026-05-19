FROM docker.elastic.co/logstash/logstash-oss:9.3.3

# Install the MQTT input and GELF output plugins
RUN logstash-plugin install logstash-input-paho-mqtt
RUN logstash-plugin install logstash-output-gelf

