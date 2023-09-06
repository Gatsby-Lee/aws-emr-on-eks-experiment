##
# @note: To improve cache re-use in image build, adding JARs goes first.
#        If "python dependencies installation" ( step3, step4 ) goes first,
#            the adding JARs less likely use the intermediate cache image since step3 and step4 has changes and doesn't hit cache.
#
# references
# - https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/docker-custom-images-steps.html
# - Base Image Region: https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/docker-custom-images-tag.html
##
# ECR us-west-2: 895885662937
FROM 895885662937.dkr.ecr.us-west-2.amazonaws.com/spark/emr-6.5.0:latest

# step 0: preparation
USER root
# step 1: install os level pkg
RUN yum -y install zip

# step 2: Add required JARs
# @note: PERMISSION: writing to JAR_HOME requires root permission,
# @note: S3 protocol doesn't work with ADD. It should be changed to `virtual-host-style` OR `aws s3 cp`
ARG JAR_HOME=/usr/lib/spark/jars/
ADD https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar $JAR_HOME
ADD https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.6.2/kafka-clients-2.6.2.jar $JAR_HOME
# Spark version related.
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.1.2/spark-sql-kafka-0-10_2.12-3.1.2.jar $JAR_HOME
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-streaming_2.12/3.1.2/spark-streaming_2.12-3.1.2.jar $JAR_HOME
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-tags_2.12/3.1.2/spark-tags_2.12-3.1.2.jar $JAR_HOME
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.1.2/spark-token-provider-kafka-0-10_2.12-3.1.2.jar $JAR_HOME
# Extra JARs like Hudi
# Update permissions
RUN chmod -R +r /usr/lib/spark/jars

### @TODO: the python dependencies installation might be packaged like below link.
# ref: https://github.com/AlexIoannides/pyspark-example-project/blob/master/build_dependencies.sh
# step 3: install third party python packages
RUN pip3 install --upgrade pip \
    && pip3 install --upgrade poetry
RUN pip3 install confluent-kafka==1.8.2
# step 4: copy over custom ETL python modules
# @note: the hadoop needs execution permission on the zip file
# @note: the compressed zip file will be referred by Spark with option --py-files
# @note: /tmp can't be used - https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/docker-custom-images-considerations.html
COPY spark_jobs /my_src/spark_jobs
RUN cd /my_src \
    && zip -r dependency_packages.zip spark_jobs/ -x "spark_jobs/main_*.py" \
    && chmod +x /my_src/dependency_packages.zip \
    && cd -

# step 5: copy Java/Spark/Hadoop related config
# step 5.1: copy custom log4j config
COPY spark_conf/log4j.properties.latest /usr/lib/spark/conf/log4j.properties

# step 6: Switch back user to hadoop
USER hadoop:hadoop
