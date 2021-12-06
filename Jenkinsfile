pipeline {

  agent { label 'azure' }

  parameters{
    string(defaultValue: 'sq,tsla', name: 'Stocks', description: 'Comma spearated list of stocks you want to analyze and watch')
  }

  stages {

    stage('Checkout') {
      steps {
          checkout scm
      }  
    }

    stage('update stock cache') {
        steps {
            script {
                    sh """
                       python3 src/cache_df.py ${params.Stocks}
                    """    
             
            }
        }
    }
  
  } 
}