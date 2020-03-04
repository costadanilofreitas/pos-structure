
# **pos-structure**

========================================================================


### **Requirements:**
 * Python 2 (last version) with PIP on windows path
 * Git on windows path
 * Git-Bash on windows path
 * NPM on windows path
 * Node.js on windows path
 
 
### **Steps to build environment:**

 - Clone the pos-structure repository (change the installation path):


    ```
    git clone --progress -v "https://bitbucket.org/edeployteam/edeploy-pos-structure.git" "YOUR_INSTALLATION_PATH_HERE"   
    ```    

 - Checkout to correct branch:

    ```
    git checkout -b new-git remotes/origin/new-git -- 
    ```

 - Go to src folder and update your submodule and checkout them to correct branch:

    ```
    cd src
    ```
    
    ```
    git submodule update --progress --init --recursive -- "src"
    ```
    
    ```
    git checkout -b new-git remotes/origin/new-git -- 
    ```
    

 - Go to pos-structure base directory and execute ```build_environment.bat```
 
 
### **Steps to run:**

  - On pos-strucute base directory, execute ```start.bat```
  
  - To see the POS interface, use your navigator to access the follow URL:
  
     <http://localhost:8080/sui/?posid=1>
 
