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
                '''
                }
        }
        stage('Deploy NA') {
            steps {
                sh '''
                    sudo SERVER=NA1 COMPOSE_PROJECT_NAME=lightshield_na1 docker-compose up --build -d
                   '''
            }
        }
        stage('Deploy EUW') {
            steps {
                sh '''
                    sudo SERVER=EUW1 COMPOSE_PROJECT_NAME=lightshield_euw1 docker-compose build
                    sudo SERVER=EUW1 COMPOSE_PROJECT_NAME=lightshield_euw1 docker-compose up -d
                   '''
            }
        }
        stage('Deploy KR') {
            steps {
                sh '''
                    sudo SERVER=KR COMPOSE_PROJECT_NAME=lightshield_kr docker-compose up --build -d
                   '''
            }
        }
    }
}
