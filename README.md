# **pos-structure**


### **Requirements:**
 * Python 2 or 3 with PIP on windows path
 * Git on windows path
 * Git-Bash on windows path
 * NPM on windows path
 * Node.js on windows path
 
 
### **Steps to build environments:**

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
    
    git submodule update --progress --init --recursive -- "src"
    
    git checkout -b new-git remotes/origin/new-git -- 
    ```
    
 - Go to scripts folder and run build.bat (this process can take a few minutes):
 
    ```
    cd ../scripts
    
    build.bat
    ```
    