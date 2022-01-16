pipeline {

  agent { label 'azure' }

  stages {

    stage('Checkout') {
      steps {
          checkout scm
      }  
    }

    stage('update portfolio listing') {
        steps {
            script {
                    sh """
                       echo Portfolio_Import
                       cd src
                       python3 import_portfolio_yahoo.py
                    """    
             
            }
        }
    }

    stage('update portfolio value') {
        steps {
            script {
                    sh """
                       echo update_portfolio_value
                       cd src
                       python3 portfolio_calc_value.py
                    """    
             
            }
        }
    }


    stage('cache my stock data in redis') {
        steps {
            script {
                    sh """
                       cd src
                       python3 cache_df.py
                    """    
             
            }
        }
    }

  
  } 
}