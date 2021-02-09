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
        stage('Deploy') {
            steps {
                sh '''
                    sudo docker-compose build
                    sudo docker-compose up -d --remove-orphans
                   '''
            }
        }
    }
}
