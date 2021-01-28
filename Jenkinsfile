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
                    sudo SERVER=na1 docker-compose build
                    sudo SERVER=na1 docker-compose up -d
                   '''
            }
        }
        stage('Deploy EUW') {
            steps {
                sh '''
                    sudo SERVER=euw1 docker-compose build
                    sudo SERVER=euw1 docker-compose up -d
                   '''
            }
        }
        stage('Deploy KR') {
            steps {
                sh '''
                    sudo SERVER=kr docker-compose up --build -d
                   '''
            }
        }
    }
}
