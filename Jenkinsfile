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
        stage('Deploy') {
            steps {
                sh '''
                    cp /services/04_lightshield_proxy/secrets.env .
                    sudo docker-compose build
                    SERVER=EUW1 sudo docker-compose -p lightshield_proxy_euw1 up -d
                   '''
            }
        }
    }
}
