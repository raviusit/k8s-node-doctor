// Author :- raviusit@gmail.com
/* groovylint-disable CompileStatic, NestedBlockDepth */
pipeline {
    options {
        disableConcurrentBuilds()
        ansiColor('xterm')
    }
    agent {
        kubernetes {
            defaultContainer 'jnlp'
            yaml"""
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: <jnlp-alpine:4.3.4>
    args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
  - name: docker
    image: <docker:19.03>
    command:
    - cat
    tty: true
    volumeMounts:
    - name: dockersock
      mountPath: /var/run/docker.sock
  imagePullSecrets:
    - name: <cicd-regcred>
  volumes:
  - name: dockersock
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }
    environment {
        PROTOCOL = 'https://'
        IMAGE_TAG =  '0.0.8'
        CONTAINER_DOCKER = 'docker'
        IMAGE_NAME = 'k8s-node-doctor'
        IMG_REPO_CREDENTIAL = <technical user>
    }
    stages {
        stage('build-jenkins-image') {
            steps {
                script {
                    container(CONTAINER_DOCKER) {
                        docker.withRegistry(PROTOCOL + IMG_REPO_URL, IMG_REPO_CREDENTIAL) {
                            sh "docker build -t $IMG_REPO_URL/$IMAGE_NAME:$IMAGE_TAG ."
                        }
                    }
                }
            }
        }
        stage('push-jenkins-image') {
            steps {
                script {
                    container(CONTAINER_DOCKER) {
                        docker.withRegistry(PROTOCOL + IMG_REPO_URL, IMG_REPO_CREDENTIAL) {
                            sh "docker push $IMG_REPO_URL/$IMAGE_NAME:$IMAGE_TAG"
                        }
                    }
                }
            }
        }
    }
}
