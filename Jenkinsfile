pipeline {

  agent { label 'ubuntu' }

  stages {

    stage('Checkout') {
      steps {
          checkout scm
      }  
    }

    stage('update stock quotes') {
        steps {
            script {
                    sh """
                       echo stockupdate
                       cd src
                       python3 cache_df-1min.py
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
