# **edeploy-pos-structure**

========================================================================

### **Requirements:**

 1. Install all the following dependencies on your latest version:

 * [Python 2 with PIP](https://www.python.org/downloads/windows/)   
 * [Git with Git-Bash](https://git-scm.com/downloads)
 * [NodeJS with NPM](https://nodejs.org/en/download/)

 2. If you installed the dependencies on a not standard directory, create a file name `set_paths.bat` and add the following content to it:

    ```
    set PYTHON_DIR=${PYTHON_DIR}
    set GIT_DIR=${GIT_DIR}
    set NODE_DIR=${NODE_DIR}
    ```
    
    Replace `${PYTHON_DIR}` with the python installation directory (default: `C:\Python27`)
    Replace `${GIT_DIR}` with the git installation directory (default: `C:\Program Files\Git`)
    Replace `${NODE_DIR}` with the node installation directory (default: `C:\Program Files\nodejs`)

**Steps to build environment:**

 1. Clone the `edeploy-pos-structure` repository:

    ```
    git clone --progress -v "https://bitbucket.org/edeployteam/edeploy-pos-structure.git"
    ```

 2. Inside of `edeploy-pos-structure`, checkout to our main development branch:

    ```
    git checkout -b dev remotes/origin/dev -- 
    ```

 3. Go to `edeploy-pos-structure` and update the src submodule:

    ```
    git submodule update --progress --init --recursive -- "src"
    ```

 4. Also in `edeploy-pos-structure` checkout the development branch:
 
    ```
    git checkout -b dev remotes/origin/dev -- 
    ```

 4. Go to `edeploy-pos-structure/scripts` and execute `build_environment.bat`

### **Steps to run:**

  1. Go to `edeploy-pos-structure` and execute `start.bat`

  2. To see the POS interface, use your navigator to access the [POS URL](http://localhost:8080/sui/?posid=1)

  3. Wait for the page load (*it can take a few minutes on the first run, depending of your hard disk speed*)