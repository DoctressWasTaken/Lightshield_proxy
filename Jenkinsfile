pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                git branch: 'master',
                credentialsId: '40e37eb6-34d9-4bc0-9d2d-d924c671ee85',
                url: 'https://github.com/LightshieldDotDev/Lightshield_proxy'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..Empty'
            }
        }
        stage('Env Setup') {
            steps {
            sh '''
                cp /services/04_lightshield_proxy/secrets.env .
                sudo docker-compose build
                '''
                }
        }
        stage('Deploy EUW') {
            steps {
                sh '''
                    SERVER=EUW1 COMPOSE_PROJECT_NAME=lightshield_euw1 sudo docker-compose up -d
                   '''
            }
        }
        stage('Deploy NA') {
            steps {
                sh '''
                    SERVER=NA1 COMPOSE_PROJECT_NAME=lightshield_na1 sudo docker-compose up -d
                   '''
            }
        }
        stage('Deploy KR') {
            steps {
                sh '''
                    SERVER=KR1 COMPOSE_PROJECT_NAME=lightshield_kr sudo docker-compose up -d
                   '''
            }
        }
    }
}
