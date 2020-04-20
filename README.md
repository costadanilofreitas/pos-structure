# **edeploy-pos-structure**

========================================================================

### **Requirements:**

 1. Install all the following dependencies on your latest version:

 * [Python 2 with PIP](https://www.python.org/downloads/windows/)   
 * [Git with Git-Bash](https://git-scm.com/downloads)
 * [NodeJS with NPM](https://nodejs.org/en/download/)

 2. Add the following paths to your [Windows Path](https://docs.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v%3Doffice.14)) (*examples to add if your choose applications default installation*):

    ```
    C:\Python27\
    ```
    
    ```
    C:\Python27\Scripts\
    ```
    
    ```
    C:\Program Files\Git\
    ```
    
    ```
    C:\Program Files\Git\cmd\
    ```
    
    ```
    C:\Program Files\nodejs\
    ```

**Steps to build environment:**

 1. Clone the `edeploy-pos-structure` repository:

    ```
    git clone --progress -v "https://bitbucket.org/edeployteam/edeploy-pos-structure.git"
    ```

 2. Inside of `edeploy-pos-structure`, checkout to our main development branch:

    ```
    git checkout -b new-git remotes/origin/new-git -- 
    ```

 3. Go to `edeploy-pos-structure/src` and update your submodule and checkout them to correct branch:

    ```
    git submodule update --progress --init --recursive -- "src"
    ```

    ```
    git checkout -b new-git remotes/origin/new-git -- 
    ```

 4. Go to `edeploy-pos-structure/scripts` and execute `build_environment.bat`

### **Steps to run:**

  1. Go to `edeploy-pos-structure` and execute `start.bat`

  2. To see the POS interface, use your navigator to access the [POS URL](http://localhost:8080/sui/?posid=1)

  3. Wait for the page load (*it can take a few minutes on the first run, depending of your hard disk speed*)