
  
# **e2e tests**  
  
========================================================================  
  
 **Requirements to execution:**  
  
1. Open your PyCharm project on the follow directory:  
	```
	mwpos\src\tests\e2e  
	```
2. Create your python interpreter using the `python.exe` existing on your project (DO NOT reuse another environment):  
	```
	mwpos\python\python.exe  
	```
3. Add the follow paths on your python interpreter:  
    ```
    mwpos\src\tests\e2e\src  
    mwpos\src\tests\e2e\lib 
    mwpos\src\tests\e2e\util
    ```
    
 **How it works:**  
  
&nbsp;&nbsp;&nbsp;&nbsp;The tests on this directory are using the `BEHAVE` to write the steps of the test on `*.feature` file.  This file, in integration with `SELENIUM PYTHON`, will provide the tools to assert your UI's verifications.  
  
&nbsp;&nbsp;&nbsp;&nbsp;Read the documentations here:  
  
 1. [Behave documentation](https://behave.readthedocs.io/en/latest/)  
 2. [Selenium Python documentation](https://selenium-python.readthedocs.io/)

 **Troubleshooting:**  
  
&nbsp;&nbsp;&nbsp;&nbsp;Verify the compatibility between your `CHROMEDRIVER/PYTHONJS` and your `GOOGLE CHROME` version. All this applications support only a range of dependencies tools versions.

&nbsp;&nbsp;&nbsp;&nbsp;By default, we are using only the `CHROMEDRIVER` on our tests. So:
	
1. [Check your GOOGLE CHROME version](chrome://settings/help);
2. [Download the CHROME DRIVER corresponding your GOOGLE CHROME version](https://chromedriver.chromium.org/downloads)
3. Update the e2e libs directory with your new CHROME DRIVER version:
	```
	mwpos\src\tests\e2e\lib\chromedriver\windows\chromedriver.exe
	```
	3a. If you are on the latest `GOOGLE CHROME` version, please commit your binary changes
