AWS EMR on EKS Experiment
=========================

Build Docker Image
------------------

.. code-block:: bash

    # ref: https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html
    # In this example, using us-west-2

    # Login Amazon ECR where the base EMR Image is stored.
    # The Base EMR Image is part of dockerfile as well.
    aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 895885662937.dkr.ecr.us-west-2.amazonaws.com

    # Login Your Amazon ECR
    aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <your-aws-account-id>.dkr.ecr.us-west-2.amazonaws.com

    # Build Image
    docker build -f dockerfile -t <your-aws-account-id>.dkr.ecr.us-west-2.amazonaws.com/<your-ecr-repo-name>:<image-tag> .

    # Push Image to Amazon ECR
    docker push <your-aws-account-id>.dkr.ecr.us-west-2.amazonaws.com/<your-ecr-repo-name>:<image-tag>


Submit Spark Job by AWS CLI
---------------------------

.. code-block:: bash

    # Update spark_jobs_config/etl-hello-world.json
    # - virtual-cluster-id
    # - execution-role-arn
    # - spark-container-image
    aws emr-containers start-job-run \
        --cli-input-json file://./spark_jobs_config/exp_custom_module_in_udf.json

    aws emr-containers list-job-runs \
        --virtual-cluster-id <virtual-cluster-id>
